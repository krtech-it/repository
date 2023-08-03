from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.orm.decl_api import DeclarativeMeta

from schemas.entity import UserCreate, UserLogin
from models.entity import User, Role, Base
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from services.role import BaseRole
from core.config import app_settings, ErrorName
from time import time


class FieldFilter(BaseModel):
    attr_name: str
    attr_value: int | str


class BaseAuth(BaseRepository, BaseAuthJWT, CacheRedis):

    async def sign_up(self, data: UserCreate) -> str | ErrorName:
        """
        Регистрирует нового пользователя.

        :param data: (UserCreate) Данные, необходимые для создания нового пользователя.
        :return:
        Union[str, ErrorName]: Возвращает строку 'Success', если регистрация прошла успешно,
                               либо объект класса ErrorName с ошибкой (например, если пользователь с таким
                               логином или email уже существует).
        """
        data_filter = [
            {
                'model': User,
                'fields': [
                    FieldFilter(attr_name='login', attr_value=data.login),
                    FieldFilter(attr_name='email', attr_value=data.email)
                ]
            },
        ]
        users = await self.get_list_obj_by_list_attr_name_operator_or(data_filter)
        for user in users.iterator:
            if user.login == data.login:
                return ErrorName.LoginAlreadyExists
            if user.email == data.email:
                return ErrorName.EmailAlreadyExists

        role = await self.get_first_obj_order_by_attr_name(Role, 'lvl')
        if role is None:
            role_manager = BaseRole(self.session)
            await role_manager.create_default_role()
            role = await self.get_first_obj_order_by_attr_name(Role, 'lvl')

        await self.create_obj(
            model=User,
            data={
                'login': data.login,
                'password': data.password,
                'last_name': data.last_name,
                'first_name': data.first_name,
                'role_id': role.id,
                'email': data.email,
            }
        )

    async def log_in(self, data: UserLogin, user_agent: str) -> None | ErrorName:
        """
         Аутентификация пользователя и создание токенов.

        :param data: (UserLogin) Данные, необходимые для аутентификации пользователя (логин и пароль).
        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        :return:
        Union[None, ErrorName]: Возвращает None, если аутентификация прошла успешно,
                                или объект класса ErrorName с ошибкой (например, если пользователь не найден
                                или неверный пароль).
        """
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            return ErrorName.DoesNotExist
        if not user.check_password(data.password):
            return ErrorName.InvalidPassword
        _, refresh_token = await self.create_tokens(sub=user.id, user_claims={
            'user_agent': user_agent,
            'is_admin': user.is_admin
            })

        await self._put_object_to_cache(obj=refresh_token, time_cache=app_settings.authjwt_time_refresh)

    async def get_info_from_access_token(self, user_agent: str) -> dict | ErrorName:
        """
        Получает информацию из access token и проверяет его безопасность.

        :param user_agent: (str) Заголовок User-Agent, для сравнения с данными из access token.
        :return:
        Union[dict, ErrorName]: Возвращает словарь с информацией из access token,
                                или объект класса ErrorName с ошибкой (например, если access token недействителен
                                или не безопасен).
        """
        user_data = await self.check_access_token()
        if await self._object_from_cache(obj=user_data.get('jti')):
            return ErrorName.InvalidAccessToken
        elif user_agent != user_data.get('user_agent'):
            time_cache = user_data.get('exp', int(time())) - int(time())
            await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)
            return ErrorName.UnsafeEntry
        else:
            return user_data

    async def refresh_token(self, user_agent: str, request: Request) -> str | ErrorName:
        """
            Обновляет access token и возвращает его.

        :param user_agent: (str) Заголовок User-Agent для идентификации клиентского приложения.
        :param request: (Request) Объект запроса, содержащий cookies с refresh token и access token.
        :return:
        Union[str, ErrorName]: Возвращает обновленный access token, если все проверки прошли успешно,
                               или объект класса ErrorName с ошибкой (например, если refresh token недействителен,
                               access token не соответствует refresh token или User-Agent не безопасен).
        """
        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        if not await self._object_from_cache(obj=refresh_token):
            return ErrorName.InvalidRefreshToken

        await self._delete_object_from_cache(obj=refresh_token)
        uuid_access = request.cookies.get(app_settings.authjwt_access_cookie_key).split('.')[-1]
        data = await self.check_refresh_token()
        if data.get('uuid_access', '') != uuid_access:
            return ErrorName.InvalidAccessRefreshTokens
        elif data.get('user_agent', '') != user_agent:
            return ErrorName.UnsafeEntry
        _, refresh_token = await self.create_tokens(
            sub=data.get('sub'),
            user_claims={
                'user_agent': user_agent,
                'is_admin': data.get('is_admin')
                })
        await self._put_object_to_cache(refresh_token, app_settings.authjwt_time_refresh)

    async def logout(self, request: Request) -> None:
        """
        Осуществляет выход пользователя из системы (logout).

        :param request: (Request) Объект запроса, содержащий cookies с данными о пользователе.
        :return:
        None: Метод не возвращает значения, а просто выполняет процесс выхода пользователя из системы.
        """
        user_data = await self.check_access_token()
        time_cache = user_data.get('exp', int(time())) - int(time())
        await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)

        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        await self._delete_object_from_cache(obj=refresh_token)

        await self.jwt_logout()


class UserManage:
    '''
    Класс для управления личным кабинетом пользователя
    '''

    def __init__(self, manager_auth: BaseAuth, manager_role: BaseRole):
        self.manager_auth = manager_auth
        self.manager_role = manager_role


    async def get_user_data(self, user_agent: str):
        user_data = await self.manager_auth.get_info_from_access_token(user_agent)
        user_id = user_data.get("sub")
        user_obj = await self.get_obj_by_attr_name(User, "id", user_id)
        return user_obj.__dict__()

from fastapi import Request

from schemas.entity import UserCreate, UserLogin, UserProfil, ChangeProfil
from models.entity import User, Role
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from services.role import BaseRole
from core.config import app_settings, ErrorName
from time import time


class BaseUser(BaseRepository, BaseAuthJWT, CacheRedis):

    async def sign_up(self, data: UserCreate) -> str | ErrorName:
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is not None:
            return ErrorName.LoginAlreadyExists
        user = await self.get_obj_by_attr_name(User, 'email', data.email)
        if user is not None:
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
        user: User = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            return ErrorName.DoesNotExist
        if not user.check_password(data.password):
            return ErrorName.InvalidPassword
        _, refresh_token = await self.create_tokens(sub=str(user.id), user_claims={
            'user_agent': user_agent,
            'is_admin': user.is_admin
            })

        await self._put_object_to_cache(obj=refresh_token, time_cache=app_settings.authjwt_time_refresh)

    async def get_info_from_access_token(self, user_agent: str) -> dict | ErrorName:
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

    def __init__(self, manager_auth: BaseUser, manager_role: BaseRole):
        self.manager_auth = manager_auth
        self.manager_role = manager_role


    async def get_user_data(self, user_agent: str):
        '''
        Метод для получения информации о пользователе.
        '''

        user_data = await self.manager_auth.get_info_from_access_token(user_agent)
        user_id = user_data.get("sub")
        user_obj: User = await self.manager_auth.get_obj_by_attr_name(User, "id", user_id)
        if isinstance(user_obj, User):
            user_profil = await self.get_user_profil(user_obj)
            return user_profil
        return user_obj #можно убрать этот return потому что функция все равно вернет None если не выполнится условие
    
    async def change_profile_user(self, user_agent: str, new_data: ChangeProfil):
        '''
        Метод для изменения информации о пользователе
        '''

        user_data = await self.manager_auth.get_info_from_access_token(user_agent)
        user_id = user_data.get("sub")
        user_obj: User = await self.manager_auth.get_obj_by_attr_name(User, "id", user_id)
        #нужна обработка ошибок для обновления БД
        if isinstance(user_obj, User):
            if new_data.login:
                user_obj.login = new_data.login
            if new_data.first_name:
                user_obj.first_name = new_data.first_name
            if new_data.last_name:
                user_obj.last_name = new_data.last_name
            if new_data.email:
                user_obj.email = new_data.email
            await self.manager_auth.session.commit()
            user_profil = await self.get_user_profil(user_obj)
            return user_profil
        return user_obj #можно убрать этот return потому что функция все равно вернет None если не выполнится условие


    async def get_user_profil(self, user_obj: User) -> UserProfil:
        role: Role = await self.manager_role.get_role(str(user_obj.role_id))
        profil = UserProfil(
            login=user_obj.login,
            first_name=user_obj.first_name,
            last_name=user_obj.last_name,
            name_role=f"{role.lvl}:{role.name_role}",
            email=user_obj.email
        )
        return profil



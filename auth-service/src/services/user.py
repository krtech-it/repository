from fastapi import Request

from schemas.entity import UserCreate, UserLogin
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
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            return ErrorName.DoesNotExist
        if not user.check_password(data.password):
            return ErrorName.InvalidPassword
        _, refresh_token = await self.create_tokens(sub=user.login, user_claims={'user_agent': user_agent})

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
        _, refresh_token = await self.create_tokens(sub=data.get('sub'), user_claims={'user_agent': user_agent})
        await self._put_object_to_cache(refresh_token, app_settings.authjwt_time_refresh)

    async def logout(self, request: Request) -> None:
        user_data = await self.check_access_token()
        time_cache = user_data.get('exp', int(time())) - int(time())
        await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)

        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        await self._delete_object_from_cache(obj=refresh_token)

        await self.jwt_logout()

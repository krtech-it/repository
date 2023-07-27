from fastapi import Request

from schemas.entity import UserCreate, UserLogin
from models.entity import User
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from core.config import app_settings
from time import time


class BaseUser(BaseRepository, BaseAuthJWT, CacheRedis):
    async def sign_up(self, data: UserCreate) -> str | None:
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            await self.create_obj(
                model=User,
                data={
                    'login': data.login,
                    'password': data.password,
                    'last_name': data.last_name,
                    'first_name': data.first_name
                }
            )
        else:
            return 'AlreadyExists'

    async def log_in(self, data: UserLogin, user_agent: str) -> None | str:
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            return 'DoesNotExist'
        if not user.check_password(data.password):
            return 'InvalidPassword'
        _, refresh_token = await self.create_tokens(sub=user.login, user_claims={'user_agent': user_agent})

        await self._put_object_to_cache(obj=refresh_token, time_cache=app_settings.authjwt_time_refresh)

    async def get_info_from_access_token(self, user_agent: str) -> dict | str:
        user_data = await self.check_access_token()
        if await self._object_from_cache(obj=user_data.get('jti')):
            return "InvalidAccessToken"
        elif user_agent != user_data.get('user_agent'):
            time_cache = user_data.get('exp', int(time())) - int(time())
            await self._put_object_to_cache(obj=user_data.get('jti'), time_cache=time_cache)
            return "UnsafeEntry"
        else:
            return user_data

    async def refresh_token(self, user_agent: str, request: Request) -> str | None:
        refresh_token = request.cookies.get(app_settings.authjwt_refresh_cookie_key)
        if not await self._object_from_cache(obj=refresh_token):
            return "InvalidRefreshToken"

        await self._delete_object_from_cache(obj=refresh_token)
        uuid_access = request.cookies.get(app_settings.authjwt_access_cookie_key).split('.')[-1]
        data = await self.check_refresh_token()
        if data.get('uuid_access', '') != uuid_access:
            return "InvalidAccessRefreshTokens"
        elif data.get('user_agent', '') != user_agent:
            return "UnsafeEntry"
        _, refresh_token = await self.create_tokens(sub=data.get('sub'), user_claims={'user_agent': user_agent})
        await self._put_object_to_cache(refresh_token, app_settings.authjwt_time_refresh)

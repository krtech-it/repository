from async_fastapi_jwt_auth import AuthJWT
from core.config import app_settings


class BaseAuthJWT:
    def __init__(self, auth: AuthJWT, **kwargs):
        self.auth = auth
        super().__init__(**kwargs)

    async def create_tokens(
            self,
            sub: str,
            user_claims: dict,
            expires_time_access: int = app_settings.authjwt_time_access,
            expires_time_refresh: int = app_settings.authjwt_time_refresh
    ) -> tuple[str]:
        access_token = await self.auth.create_access_token(
            subject=sub, expires_time=expires_time_access, user_claims=user_claims
        )
        uuid_access = access_token.split('.')[-1]
        user_claims['uuid_access'] = uuid_access
        refresh_token = await self.auth.create_refresh_token(
            subject=sub, expires_time=expires_time_refresh, user_claims=user_claims
        )
        await self.auth.set_access_cookies(access_token)
        await self.auth.set_refresh_cookies(refresh_token)
        return access_token, refresh_token

    async def check_access_token(self) -> dict:
        await self.auth.jwt_required()
        user_data = await self.auth.get_raw_jwt()
        return user_data

    async def check_refresh_token(self) -> dict:
        await self.auth.jwt_refresh_token_required()
        user_data = await self.auth.get_raw_jwt()
        return user_data

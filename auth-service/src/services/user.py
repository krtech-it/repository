import uuid

from async_fastapi_jwt_auth import AuthJWT

from schemas.entity import UserCreate, UserLogin
from models.entity import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.postgres import Base


class BaseRepository:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        super().__init__(**kwargs)

    async def get_obj_by_attr_name(self, model: Base, attr_name: str, attr_value: str | int) -> Base | None:
        query = select(model).filter(getattr(model, attr_name) == attr_value)
        obj = await self.session.execute(query)
        obj = obj.scalar()
        return obj

    async def create_obj(self, model: Base, data: dict) -> None:
        new_user = model(
            **data
        )
        self.session.add(new_user)
        await self.session.commit()


class BaseAuthJWT:
    def __init__(self, auth: AuthJWT):
        self.auth = auth

    async def create_tokens(self, sub: str, user_claims: dict) -> tuple[str]:
        shared_key = str(uuid.uuid4())
        user_claims['shared_key'] = shared_key
        access_token = await self.auth.create_access_token(subject=sub, user_claims=user_claims)
        refresh_token = await self.auth.create_refresh_token(subject=sub, user_claims=user_claims)
        await self.auth.set_access_cookies(access_token)
        return access_token, refresh_token

    async def check_access_token(self):
        await self.auth.jwt_required()
        user_data = await self.auth.get_raw_jwt()
        return user_data


class BaseUser(BaseRepository, BaseAuthJWT):
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

    async def log_in(self, data: UserLogin, user_agent: str) -> dict:
        user = await self.get_obj_by_attr_name(User, 'login', data.login)
        if user is None:
            return 'DoesNotExist'
        if not user.check_password(data.password):
            return 'InvalidPassword'
        _, refresh_token = await self.create_tokens(sub=user.login, user_claims={'user_agent': user_agent})

        # добавить в редис рефреш токен
        return {"refresh_token": refresh_token}

    async def get_info_from_access_token(self):
        user_data = await self.check_access_token()
        return user_data

from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from services.user import BaseUser
from services.role import BaseRole
from db.postgres import get_session
from db.redis import get_redis, Redis


def get_repository_user(
        session: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis: Redis = Depends(get_redis)
):
    return BaseUser(session=session, auth=authorize, redis=redis)


def get_repository_role(
        session: AsyncSession = Depends(get_session)
):
    return BaseRole(session=session)
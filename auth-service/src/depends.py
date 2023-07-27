from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from services.user import BaseUser
from db.postgres import get_session
from db.redis import get_redis, Redis


def get_repository_user(session: AsyncSession = Depends(get_session), Authorize: AuthJWT = Depends(), redis: Redis = Depends(get_redis)):
    return BaseUser(session=session, auth=Authorize, redis=redis)

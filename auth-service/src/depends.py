from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from services.user import BaseUser
from db.postgres import get_session


def get_repository_user(session: AsyncSession = Depends(get_session)):
    return BaseUser(session=session)

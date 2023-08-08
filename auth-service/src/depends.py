from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from services.user import BaseAuth, UserManage
from services.role import BaseRole
from services.history import BaseHistory 
from services.admin import BaseAdmin
from db.postgres import get_session
from db.redis import get_redis, Redis


def get_manager_history(
    session: AsyncSession = Depends(get_session)
):
    return BaseHistory(session=session)


def get_repository_user(
        session: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(),
        redis: Redis = Depends(get_redis),
        manager_history: BaseHistory = Depends(get_manager_history)
):
    return BaseAuth(session=session, auth=authorize, redis=redis, manager_history=manager_history)


def get_repository_role(
        session: AsyncSession = Depends(get_session)
):
    return BaseRole(session=session)


def get_admin(
        manager_auth: BaseAuth = Depends(get_repository_user),
        manager_role: BaseRole = Depends(get_repository_role)
):
    return BaseAdmin(manager_auth=manager_auth, manager_role=manager_role)


def get_user_manage(
        manager_auth: BaseAuth = Depends(get_repository_user),
        manager_role: BaseRole = Depends(get_repository_role),
        manager_history: BaseHistory = Depends(get_manager_history)
):
    return UserManage(manager_auth=manager_auth, manager_role=manager_role, manager_history=manager_history)
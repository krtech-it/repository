import uuid

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Cookie
from typing import Annotated
from depends import get_repository_user, get_repository_role, get_admin
from models.entity import Role
from schemas.entity import UserCreate, UserLogin, RoleCreate, UserRole
from services.user import BaseAuth
from services.role import BaseRole
from services.admin import BaseAdmin
from core.config import ErrorName

router = APIRouter()


@router.patch('/create/')
async def add_role(
        data: RoleCreate, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    result = await manager_auth.get_info_from_access_token(user_agent)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')

    if result.get('is_admin'):
        status = await admin_manager.create_role(data)
        match status:
            case ErrorName.RoleAlreadyExists:
                raise HTTPException(status_code=400, detail='Такая роль уже существует')
        return RoleCreate(**status)


@router.patch("/update/{role_id}/")
async def update_role(
        role_id: uuid.UUID,
        data: RoleCreate, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    result = await manager_auth.get_info_from_access_token(user_agent)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
    if result.get('is_admin'):
        status = await admin_manager.update_role(role_id=role_id, new_data=data)
        match status:
            case ErrorName.RoleDoesNotExist:
                raise HTTPException(status_code=400, detail='Такой роли не существует')
        return status


@router.post('/assign/')
async def assign_role(
        data: UserRole, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    result = await manager_auth.get_info_from_access_token(user_agent)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
    if result.get('is_admin'):
        status = await admin_manager.assign_role(role_id=data.role_id, user_id=data.user_id)
        match status:
            case ErrorName.RoleDoesNotExist:
                raise HTTPException(status_code=400, detail='Такой роли не существует')
            case ErrorName.UserDoesNotExist:
                raise HTTPException(status_code=400, detail='Такого пользователя не существует')
            case ErrorName.DoesNotExist:
                raise HTTPException(status_code=400, detail='Такого пользователя и такой роли не существует')
        return 'role assigned'


@router.patch("/delete/{role_id}/")
async def delete_role(
        role_id: uuid.UUID, user_agent: Annotated[str | None, Header()] = None,
        manager_auth: BaseAuth = Depends(get_repository_user),
        admin_manager: BaseAdmin = Depends(get_admin)
):
    result = await manager_auth.get_info_from_access_token(user_agent)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
    if result.get('is_admin'):
        await admin_manager.delete_role(role_id)
        return "role deleted"

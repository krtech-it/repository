from services.user import UserManage

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Cookie
from typing import Annotated
from depends import get_repository_user, get_repository_role, get_user_manage
from schemas.entity import UserCreate, UserLogin, UserProfil, ChangeProfil
from services.user import BaseUser
from services.role import BaseRole
from core.config import ErrorName


router = APIRouter()


@router.get('/self_data/')
async def profil_user(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод возвращает информацию о пользователе.
    '''

    user_profil = await user_manager.get_user_data(user_agent) #user_profile
    match user_profil:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
    return user_profil


@router.patch('/self_data/')
async def profil_user(
        self_data: ChangeProfil,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод для редактирования профиля пользователя.
    '''

    user_profil = await user_manager.change_profile_user(user_agent, self_data)
    match user_profil:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
    return user_profil
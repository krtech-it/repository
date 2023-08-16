from services.user import UserManage

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Annotated
from depends import get_user_manage
from schemas.entity import UserProfil, ChangeProfil, ChangePassword, HistoryUser, ChangeLevel
from core.config import ErrorName


router = APIRouter()


@router.get('/self_data/')
async def profil_user(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод возвращает информацию о пользователе.
    '''

    user_profil: UserProfil = await user_manager.get_user_data(user_agent)
    match user_profil:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
    return user_profil


@router.patch('/self_data/')
async def profile_user(
        self_data: ChangeProfil,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> UserProfil:
    '''
    Метод для редактирования профиля пользователя.
    '''

    user_profil: UserProfil = await user_manager.change_profile_user(user_agent, self_data)
    match user_profil:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.LoginAlreadyExists:
            raise HTTPException(status_code=400, detail='Пользователь с таким login уже существует')
        case ErrorName.EmailAlreadyExists:
            raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')
    return user_profil


@router.post('/change_password/')
async def change_password(
        self_data: ChangePassword,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> str:
    '''
    Метод для редактирования профиля пользователя.
    '''

    user_profil: UserProfil = await user_manager.change_password(user_agent, self_data)
    match user_profil:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidPassword:
            raise HTTPException(status_code=400, detail='Неверный пароль')
    return "password changed"


@router.get('/get_history/')
async def get_history(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)
) -> list[HistoryUser]:
    '''
    Метод возвращает информацию о пользователе.
    '''

    user_history: UserProfil = await user_manager.get_history(user_agent)
    match user_history:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
    return user_history


@router.post('/change-level/')
async def change_level(
        self_data: ChangeLevel,
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)) -> str | None:
    '''
    Метод для редактирования профиля пользователя.
    '''
    status = await user_manager.change_level(user_agent, self_data.level_up)
    match status:
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.RoleDoesNotExist:
            raise HTTPException(status_code=400, detail='Роли не существует')
    return "level raised" if self_data.level_up else "decreased"

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Cookie
from typing import Annotated
from depends import get_repository_user
from schemas.entity import UserCreate, UserLogin
from services.user import BaseUser
from core.config import ErrorName

router = APIRouter()


@router.post('/login/')
async def login(
        data: UserLogin, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseUser = Depends(get_repository_user)
):
    user = await user_manager.log_in(data, user_agent)
    match user:
        case ErrorName.DoesNotExist:
            raise HTTPException(status_code=400, detail='Пользователя не существует')
        case ErrorName.InvalidPassword:
            raise HTTPException(status_code=400, detail='Неверный пароль')


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseUser = Depends(get_repository_user)):
    status = await user_manager.sign_up(data)
    match status:
        case ErrorName.AlreadyExists:
            raise HTTPException(status_code=400, detail='Пользователь с таким login уже существует')


@router.get('/get_user/')
async def get_user(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseUser = Depends(get_repository_user)
):
    result = await user_manager.get_info_from_access_token(user_agent)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
    return result


@router.post('/refresh/')
async def refresh(
        request: Request, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseUser = Depends(get_repository_user),
):
    result = await user_manager.refresh_token(user_agent, request)
    match result:
        case ErrorName.UnsafeEntry:
            raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')
        case ErrorName.InvalidAccessRefreshTokens:
            raise HTTPException(status_code=422, detail='access токен не принадлежит refresh токену')
        case ErrorName.InvalidRefreshToken:
            raise HTTPException(status_code=422, detail='Signature has expired')
    return result


@router.get('/logout/')
async def logout(request: Request, user_manager: BaseUser = Depends(get_repository_user)):
    await user_manager.logout(request)

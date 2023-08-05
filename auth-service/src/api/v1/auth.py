from fastapi import APIRouter, Depends, HTTPException, Header, Request, Cookie
from typing import Annotated
from depends import get_repository_user, get_repository_role
from schemas.entity import UserCreate, UserLogin
from services.user import BaseAuth
from services.role import BaseRole
from core.config import ErrorName

router = APIRouter()


@router.post('/login/')
async def login(
        data: UserLogin, user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user)
):
    user = await user_manager.log_in(data, user_agent)
    match user:
        case ErrorName.DoesNotExist:
            raise HTTPException(status_code=400, detail='Пользователя не существует')
        case ErrorName.InvalidPassword:
            raise HTTPException(status_code=400, detail='Неверный пароль')


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseAuth = Depends(get_repository_user)):
    status = await user_manager.sign_up(data)
    match status:
        case ErrorName.LoginAlreadyExists:
            raise HTTPException(status_code=400, detail='Пользователь с таким login уже существует')
        case ErrorName.EmailAlreadyExists:
            raise HTTPException(status_code=400, detail='Пользователь с таким email уже существует')
        case ErrorName.DefaultRoleDoesNotExists:
            raise HTTPException(status_code=400, detail='Нет стандартной роли, не удается создать пользователя')


@router.get('/get_user/')
async def get_user(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: BaseAuth = Depends(get_repository_user)
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
        user_manager: BaseAuth = Depends(get_repository_user),
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
async def logout(request: Request, user_agent: Annotated[str | None,
        Header()] = None, user_manager: BaseAuth = Depends(get_repository_user)):
    await user_manager.logout(request, user_agent)

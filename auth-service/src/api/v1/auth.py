from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Annotated
from depends import get_repository_user
from schemas.entity import UserCreate, UserLogin
from services.user import BaseUser

router = APIRouter()


@router.post('/login/')
async def login(data: UserLogin, user_agent: Annotated[str | None, Header()] = None, user_manager: BaseUser = Depends(get_repository_user)):
    user = await user_manager.log_in(data, user_agent)
    match user:
        case "DoesNotExist":
            raise HTTPException(status_code=400, detail='Пользователя не существует')
        case "InvalidPassword":
            raise HTTPException(status_code=400, detail='Неверный пароль')
    return user


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseUser = Depends(get_repository_user)):
    status = await user_manager.sign_up(data)
    match status:
        case "AlreadyExists":
            raise HTTPException(status_code=400, detail='Пользователь с таким login уже существует')


@router.get('/get_user/')
async def get_user(user_agent: Annotated[str | None, Header()] = None, user_manager: BaseUser = Depends(get_repository_user)):
    result = await user_manager.get_info_from_access_token()
    if user_agent == result.get('user_agent'):
        return result
    # прописать логику добавления токенов в черный список в редис чтобы по ним больше нельзя было заходить
    raise HTTPException(status_code=400, detail='подозрение на небезопасный вход')

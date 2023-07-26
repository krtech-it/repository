from fastapi import APIRouter, Depends, HTTPException
from services.user import BaseUser
from depends import get_repository_user
from schemas.entity import UserCreate, UserLogin
router = APIRouter()


@router.post('/')
async def login(data: UserLogin, user_manager: BaseUser = Depends(get_repository_user), Authorize: AuthJWT = Depends()):
    user = await user_manager.log_in(data, Authorize)
    match user:
        case "DoesNotExist":
            raise HTTPException(status_code=400, detail='Пользователя не существует')
        case "InvalidPassword":
            raise HTTPException(status_code=400, detail='Неверный пароль')
    return user


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseUser = Depends(get_repository_user)):
    status = await user_manager.create_obj(data)
    match status:
        case "AlreadyExists":
            raise HTTPException(status_code=400, detail='Пользовательс таким login уже существует')

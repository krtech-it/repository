from fastapi import APIRouter, Depends, HTTPException
from services.user import BaseUser
from depends import get_repository_user
from schemas.entity import UserCreate, UserLogin
router = APIRouter()


@router.post('/')
async def login(data: UserLogin, user_manager: BaseUser = Depends(get_repository_user)):
    print(data.login)
    user = await user_manager.find_user(data.login)
    #session: AsyncSession = Depends(get_session)
    #user_agent: BaseUser = Depends(get_repository_user),
    # await user_agent.get_obj()
    return user


@router.post('/sign_up/')
async def sign_up(data: UserCreate, user_manager: BaseUser = Depends(get_repository_user)):
    try:
        await user_manager.create_obj(data)
    except Exception:
        raise HTTPException(status_code=400, detail='ERRROR')

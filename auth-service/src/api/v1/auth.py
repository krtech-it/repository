from fastapi import APIRouter, Depends
from services.user import BaseUser
from depends import get_repository_user
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.entity import UserInDB
from db.postgres import get_session

router = APIRouter()


@router.get('/')
async def login(session: AsyncSession = Depends(get_session)):
    user_maneger = BaseUser()
    await user_maneger.get_obj(session)
    #session: AsyncSession = Depends(get_session)
    #user_agent: BaseUser = Depends(get_repository_user),
    # await user_agent.get_obj()
    return {1:2}
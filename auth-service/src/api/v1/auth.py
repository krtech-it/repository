from fastapi import APIRouter, Depends
from services.user import BaseUser
from depends import get_repository_user

from schemas.entity import UserInDB

router = APIRouter()


@router.get('/')
async def login(user_agent: BaseUser = Depends(get_repository_user)) -> UserInDB | None:
    return user_agent.get_obj()

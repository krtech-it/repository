from services.user import UserManage

from fastapi import APIRouter, Depends, HTTPException, Header, Request, Cookie
from typing import Annotated
from depends import get_repository_user, get_repository_role, get_user_manage
from schemas.entity import UserCreate, UserLogin
from services.user import BaseAuth
from services.role import BaseRole
from core.config import ErrorName


router = APIRouter()


@router.get('/profil/')
async def profil_user(
        user_agent: Annotated[str | None, Header()] = None,
        user_manager: UserManage = Depends(get_user_manage)):
    pass
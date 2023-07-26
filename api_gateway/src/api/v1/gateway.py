from typing import Annotated

from fastapi import APIRouter, Header, Response, Request
import requests

from core.config import app_settings
from schemas.entity import UserLogin, UserCreate

router = APIRouter()


@router.post('/login/')
async def login(response: Response, data: UserLogin, user_agent: Annotated[str | None, Header()] = None):
    url = f'{app_settings.auth_url}/api/v1/auth/login/'
    headers = {
        'User-Agent': user_agent,
    }

    response_auth = requests.post(url=url, json=data.dict(), headers=headers)

    for cookie in response_auth.cookies.items():
        response.set_cookie(key=cookie[0], value=cookie[1])
    body = response_auth.json()
    return body


@router.post('/sign_up/')
async def login(data: UserCreate):
    url = f'{app_settings.auth_url}/api/v1/auth/sign_up/'
    response_auth = requests.post(url=url, json=data.dict())
    body = response_auth.json()
    return body


@router.get('/get_user/')
async def login(request: Request, user_agent: Annotated[str | None, Header()] = None):
    url = f'{app_settings.auth_url}/api/v1/auth/get_user/'
    headers = {
        'User-Agent': user_agent,
    }

    response_auth = requests.get(url=url, headers=headers, cookies=request.cookies)
    body = response_auth.json()
    return body

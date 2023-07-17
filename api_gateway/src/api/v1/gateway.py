from fastapi import APIRouter
import httpx

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    # x = {'auth': app_settings.url_auth}
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8020/api/v1/login')
        data = response.status_code
        body = response.content
        print('-------------------------------')
        print(data)
        print(body)
        print('-------------------------------')
    return {1: 2}

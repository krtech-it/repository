from fastapi import APIRouter
import requests

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    # x = {'auth': app_settings.url_auth}
    response = requests.get(f'{app_settings.auth_url}/api/v1/login')
    body = response.json()
    return body

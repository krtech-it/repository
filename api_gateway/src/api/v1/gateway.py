from fastapi import APIRouter
import requests

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    # x = {'auth': app_settings.url_auth}
    print(app_settings.url_auth)
    x = requests.get(f'{app_settings.url_auth}/api/v1/login/').json()
    return x

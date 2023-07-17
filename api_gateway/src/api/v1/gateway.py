from fastapi import APIRouter
import requests

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    # x = {'auth': app_settings.url_auth}
    x = requests.get('0.0.0.0:8020/api/v1/login/').json()
    return x

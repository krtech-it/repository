from fastapi import APIRouter
import requests

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    x = {'auth': app_settings.url_auth, 'postgres': app_settings.postgres_host}
    # x = requests.get(app_settings.url_auth).json()
    return x

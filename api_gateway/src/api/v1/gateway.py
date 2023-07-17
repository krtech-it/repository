from fastapi import APIRouter
import requests

from core.config import app_settings

router = APIRouter()


@router.get('/login/')
async def login():
    # x = {'auth': app_settings.url_auth}
    response = requests.get('http://176.124.198.110:8010/api/v1/login')
    data = response.status_code
    body = response.json()
    print('-------------------------------')
    print(data)
    print(body)
    print('-------------------------------')
    return body

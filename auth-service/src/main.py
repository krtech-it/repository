import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from core.config import app_settings as settings
from db import redis
from db.postgres import create_database

from api.v1 import auth


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    from models.entity import User
    await create_database()

app.include_router(auth.router, prefix='/api/v1/login', tags=['login'])

# if __name__ == '__main__':
#     uvicorn.run(
#         'main:app',
#         host='0.0.0.0',
#         port=8000,
#     )
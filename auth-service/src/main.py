from contextlib import asynccontextmanager

import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

# from api.v1 import films, genres, persons
from core.config import app_settings as settings
from db import redis, postgres
from db.postgres import create_database


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

# app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
# app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
# app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )
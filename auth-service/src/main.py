from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
import uvicorn
from fastapi import FastAPI, Request, status
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException

from core.config import app_settings
from db import redis
from db.postgres import create_database

from api.v1 import auth, personal_acc, roles

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


app = FastAPI(
    title=app_settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@AuthJWT.load_config
def get_config():
    return app_settings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


@app.on_event('startup')
async def startup():
    redis.redis = Redis(host=app_settings.redis_host, port=app_settings.redis_port)
    # from models.entity import User
    # await create_database()

app.include_router(auth.router, prefix='/api/v1/auth', tags=['login'])
app.include_router(personal_acc.router, prefix='/api/v1/profil', tags=['personal_acc'])
app.include_router(roles.router, prefix='/api/v1/admin', tags=['admin'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )



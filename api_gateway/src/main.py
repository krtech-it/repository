from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from core.config import app_settings as settings

from api.v1 import gateway


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(gateway.router, prefix='/api/v1', tags=['login'])

# if __name__ == '__main__':
#     uvicorn.run(
#         'main:app',
#         host='0.0.0.0',
#         port=8000,
#     )

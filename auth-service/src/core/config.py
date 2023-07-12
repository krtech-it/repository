import os
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: int = Field(..., env='POSTGRES_PORT')

    class Config:
        env_file = '.env'


app_settings = Settings()
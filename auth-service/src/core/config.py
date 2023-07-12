from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')
    postgres_host: str = Field(..., env='POSTGRES_HOST')
    postgres_port: int = Field(..., env='POSTGRES_PORT')
    database_dsn: str = Field(..., env='DATABASE_DSN')
    project_name: str = Field(..., env='PROJECT_NAME')

    class Config:
        env_file = '.env'


app_settings = Settings()
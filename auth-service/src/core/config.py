from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(..., env='REDIS_PORT')
    pg_host: str = Field(..., env='POSTGRES_HOST')
    pg_port: str = Field(..., env='POSTGRES_PORT')
    pg_user: str = Field(...,env='POSTGRES_USER')
    pg_db: str = Field(...,env='POSTGRES_DB')
    pg_password: str = Field(..., env="POSTGRES_PASSWORD")
    project_name: str = Field(..., env='PROJECT_NAME')

    class Config:
        env_file = '.env'

    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_host}/{self.pg_port}"

app_settings = Settings()

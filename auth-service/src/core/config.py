from pydantic_settings import BaseSettings
from os import getenv


class Settings(BaseSettings):
    redis_host: str 
    redis_port: int 
    pg_host: str
    pg_port: str 
    pg_user: str
    pg_db: str
    pg_password: str
    project_name: str

    def __init__(self, **data):
        data["pg_user"] = getenv("POSTGRES_USER")
        data['pg_password'] = getenv("POSTGRES_PASSWORD")
        data["pg_host"] = getenv("POSTGRES_HOST")
        data["pg_port"] = getenv("POSTGRES_PORT")
        data["pg_db"] = getenv("POSTGRES_DB")
        data["redis_host"] = getenv("REDIS_HOST")
        data["redis_port"] = getenv("REDIS_PORT")
        data["project_name"] = getenv("PROJECT_NAME")
        super().__init__(**data)
        
    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


app_settings = Settings()

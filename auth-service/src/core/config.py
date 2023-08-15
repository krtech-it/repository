from pydantic import BaseModel
from os import getenv
from dotenv import load_dotenv
from enum import Enum

load_dotenv()


class Settings(BaseModel):
    redis_host: str
    redis_port: int
    pg_host: str
    pg_port: str
    pg_user: str
    pg_db: str
    pg_password: str
    project_name: str
    authjwt_secret_key: str
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_access_cookie_key: str = 'access_token_cookie'
    authjwt_refresh_cookie_key: str = 'refresh_token_cookie'
    authjwt_time_access: int
    authjwt_time_refresh: int

    def __init__(self, **data):
        data["pg_user"] = getenv("POSTGRES_USER")
        data['pg_password'] = getenv("POSTGRES_PASSWORD")
        data["pg_host"] = getenv("POSTGRES_HOST")
        data["pg_port"] = getenv("POSTGRES_PORT")
        data["pg_db"] = getenv("POSTGRES_DB")
        data["redis_host"] = getenv("REDIS_HOST")
        data["redis_port"] = getenv("REDIS_PORT")
        data["project_name"] = getenv("PROJECT_NAME")
        data["authjwt_secret_key"] = getenv("SECRET_KEY")
        data["authjwt_time_access"] = getenv("TIME_LIFE_ACCESS")
        data["authjwt_time_refresh"] = getenv("TIME_LIFE_REFRESH")
        super().__init__(**data)

    def database_dsn(self):
        return f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


class ErrorName(Enum):
    DoesNotExist = "DoesNotExist"
    InvalidPassword = "InvalidPassword"
    LoginAlreadyExists = "LoginAlreadyExists"
    EmailAlreadyExists = "EmailAlreadyExists"
    UnsafeEntry = "UnsafeEntry"
    InvalidAccessToken = "InvalidAccessToken"
    InvalidAccessRefreshTokens = "InvalidAccessRefreshTokens"
    InvalidRefreshToken = "InvalidRefreshToken"
    DefaultRoleDoesNotExists = "DefaultRoleDoesNotExists"
    RoleAlreadyExists = "RoleAlreadyExists"
    RoleDoesNotExist = "RoleDoesNotExist"
    UserDoesNotExist = "UserDoesNotExist"


app_settings = Settings()

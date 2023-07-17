from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')

    class Config:
        env_file = '.env'


app_settings = Settings()
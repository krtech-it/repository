from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    auth_port: str = os.getenv('URL_PORT')
    auth_url: str = os.getenv('URL_AUTH')

    def __init__(self, **data):
        super().__init__(**data)
        self.auth_url = f'http://{self.auth_url}:{self.auth_port}'

    class Config:
        env_file = '.env'


app_settings = Settings()

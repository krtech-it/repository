from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    auth_url: str = 'auth_api'
    auth_port: str = '8010'
    # auth_url: str = Field(..., env='URL_AUTH')
    # auth_port: str = Field(..., env='PORT_AUTH')

    def __init__(self, **data):
        super().__init__(**data)
        self.auth_url = f'http://{self.auth_url}:{self.auth_port}'

    class Config:
        env_file = '.env'


app_settings = Settings()
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    url_auth: str = os.getenv('URL_AUTH')

    def __init__(self, **data):
        super().__init__(**data)
        self.url_auth = f'http://{self.url_auth}:8020'

    class Config:
        env_file = '.env'


app_settings = Settings()
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    project_name: str = os.getenv('PROJECT_NAME')
    auth_port: str = os.getenv('URL_PORT')
    auth_url: str = os.getenv('URL_AUTH')

    def __init__(self, **data):
        super().__init__(**data)
        self.auth_url = f'http://{self.auth_url}:{self.auth_port}'

    class Config:
        env_file = '.env'


app_settings = Settings()

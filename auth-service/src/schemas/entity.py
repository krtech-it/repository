from uuid import UUID
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str

    @field_validator('password')
    def validate_password(self, value):
        pattern = r'[a-zA-Z\d]'
        if not re.match(pattern, value):
            raise ValueError('слишком простой пароль')
        return value


class UserLogin(BaseModel):
    login: str
    password: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True

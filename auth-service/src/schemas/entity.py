from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field
# import re


class FieldFilter(BaseModel):
    attr_name: str
    attr_value: int | str


class HistoryUser(BaseModel):
    id: UUID
    time: datetime
    browser: str
    user_id: UUID
    result: bool


class UserCreate(BaseModel):
    login: str
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    email: str

class UserProfil(BaseModel):
    login: str
    first_name: str
    last_name: str
    name_role: str
    email: str

class ChangeProfil(BaseModel):
    login: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = Field(regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)

class UserLogin(BaseModel):
    login: str
    password: str

class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

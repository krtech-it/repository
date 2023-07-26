from uuid import UUID
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    login: str
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    login: str
    password: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

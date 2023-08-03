from uuid import UUID
from pydantic import BaseModel, Field


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
    email: str | None = None

class UserLogin(BaseModel):
    login: str
    password: str


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        from_attributes = True

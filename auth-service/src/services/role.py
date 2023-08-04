from fastapi import Request

from schemas.entity import UserCreate, UserLogin
from models.entity import User, Role
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from core.config import app_settings, ErrorName
from time import time

import uuid


class BaseRole(BaseRepository):

    async def create_default_role(self):
        '''
        Метод для создания роли по умолчанию
        '''
        null_role = {
            "lvl": 0,
            "name_role": "default_role",
            "description": "basic role, created automatically",
            "max_year": 1980
        }
        await self.create_obj(Role, null_role)


    async def get_role(self, id: uuid.UUID):
        '''
        Метод для получения имени роли по id
        '''

        role = await self.get_obj_by_attr_name(Role, "id", id)
        return role

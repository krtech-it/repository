import uuid

from fastapi import Request
from pydantic import BaseModel
# from sqlalchemy.orm.decl_api import DeclarativeMeta


from schemas.entity import UserCreate, UserLogin, UserProfil, ChangeProfil, ChangePassword
from models.entity import History as HistoryDB
from services.repository import BaseRepository
from services.auth_jwt import BaseAuthJWT
from services.redis_cache import CacheRedis
from services.role import BaseRole
from core.config import app_settings, ErrorName
from time import time
from werkzeug.security import generate_password_hash


class BaseHistory(BaseRepository):
    async def write_entry_history(self, user_id: uuid.UUID, user_agent: str, event_type: str, result: bool):
        await self.create_obj(
            model=HistoryDB,
            data={
                'user_id': user_id,
                'browser': user_agent,
                'event_type': event_type,
                'result': result
            }
        )

    def read_history(self):
        pass

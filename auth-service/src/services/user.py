from abc import ABC, abstractmethod
from schemas.entity import UserInDB
from models.entity import User
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    @abstractmethod
    async def get_obj(self):
        pass


class BaseUser(BaseRepository):
    async def get_obj(self):
        # y = self.session.get(User, 'c205cd9d-faad-4d7f-9368-c2c26d6126f4')
        print(type(self.session))
        return UserInDB(
            id='a72eaaec-bf37-43c6-9493-68e1ee6778ed',
            first_name='hello',
            last_name='world'
        )

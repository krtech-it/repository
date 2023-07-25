from abc import ABC, abstractmethod
from schemas.entity import UserInDB


class BaseRepository(ABC):
    def __init__(self, session):
        self.session = session

    @abstractmethod
    def get_obj(self):
        pass


class BaseUser(BaseRepository):
    def get_obj(self):
        return UserInDB(
            id='12312',
            first_name='hello',
            last_name='world'
        )

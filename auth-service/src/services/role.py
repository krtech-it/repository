from models.entity import Role
from services.repository import BaseRepository


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

    async def get_role(self, id: str) -> Role:
        '''
        Метод для получения имени роли по id
        '''

        role = await self.get_obj_by_attr_name(Role, "id", id)
        return role

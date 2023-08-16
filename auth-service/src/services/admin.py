import uuid

from schemas.entity import RoleCreate
from models.entity import User, Role
from services.repository import BaseRepository
from core.config import ErrorName


class BaseAdmin(BaseRepository):
    '''
    Класс для методов администратора
    '''

    def __init__(self, manager_auth, manager_role, *args, **kwargs):
        self.manager_auth = manager_auth
        self.manager_role = manager_role
        super().__init__(*args, **kwargs)

    async def create_role(self, data: RoleCreate):
        role = await self.manager_auth.get_obj_by_attr_name(Role, 'lvl', data.lvl)
        if role:
            return ErrorName.RoleAlreadyExists
        new_role = {
            "lvl": data.lvl,
            "name_role": data.name_role,
            "description": data.description,
            "max_year": data.max_year
        }
        await self.create_obj(Role, new_role)
        return new_role

    async def update_role(self, role_id: uuid.UUID, new_data: RoleCreate):
        role_obj: Role = await self.get_obj_by_attr_name(Role, "id", role_id)
        dict_data = dict(new_data)
        if role_obj:
            for attr, value in dict_data.items():
                if value:
                    setattr(role_obj, attr, value)
            await self.manager_auth.session.commit()
            return RoleCreate(**vars(role_obj))
        else:
            return ErrorName.RoleDoesNotExist

    async def assign_role(self, role_id: uuid.UUID, user_id: uuid.UUID):
        user_obj: User = await self.get_obj_by_pk(User, user_id)
        role_obj: Role = await self.get_obj_by_attr_name(Role, "id", role_id)
        if role_obj and user_obj:
            user_obj.role_id = role_id
            await self.manager_auth.session.commit()
        elif not role_obj:
            return ErrorName.RoleDoesNotExist
        elif not user_obj:
            return ErrorName.UserDoesNotExist
        else:
            return ErrorName.DoesNotExist

    async def delete_role(self, role_id: uuid.UUID):
        await self.delete_obj(Role, role_id)

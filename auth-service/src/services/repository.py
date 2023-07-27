from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.postgres import Base


class BaseRepository:
    def __init__(self, session: AsyncSession, **kwargs):
        self.session = session
        super().__init__(**kwargs)

    async def get_obj_by_attr_name(self, model: Base, attr_name: str, attr_value: str | int) -> Base | None:
        query = select(model).filter(getattr(model, attr_name) == attr_value)
        obj = await self.session.execute(query)
        obj = obj.scalar()
        return obj

    async def create_obj(self, model: Base, data: dict) -> None:
        new_user = model(
            **data
        )
        self.session.add(new_user)
        await self.session.commit()

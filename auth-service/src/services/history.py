import uuid

from schemas.entity import FieldFilter, HistoryUser
from models.entity import History as HistoryDB
from services.repository import BaseRepository


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

    async def get_history(self, user_id: uuid.UUID):
        data_filter = [
            {
                'model': HistoryDB,
                'fields': [
                    FieldFilter(attr_name='user_id', attr_value=str(user_id))
                ]
            },
        ]
        list_obj = await self.get_list_obj_by_list_attr_name_operator_or(data_filter)
        result = [HistoryUser.parse_obj(obj.__dict__) for obj in list_obj]
        return result

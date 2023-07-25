from functools import lru_cache

from services.user import BaseUser
from db.postgres import get_session


def get_repository_user():
    return BaseUser(session=get_session())

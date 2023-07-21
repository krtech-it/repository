import uuid
from datetime import datetime
import enum
from sqlalchemy import Boolean, Column, DateTime, String, Enum
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class RoleEnum(enum.Enum):
    adult = "adult"
    child = "child"


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_name = Column(String(255), unique=True, nullable=False)
    subscription = Column(Boolean, nullable=False)
    type = Column(Enum(RoleEnum))

    def __init__(self, user_name: str, subscription: bool, type: enum) -> None:
        self.user_name = user_name
        self.subscription = subscription
        self.type = type

    def __repr__(self) -> str:
        return f'<User {self.user_name}>'


class EventEnum(enum.Enum):
    login = "login"
    logout = "logout"
    refresh = "refresh"


class History(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_name = Column(String(255), unique=True, nullable=False)
    time = Column(DateTime, default=datetime.utcnow)
    browser = Column(String(255), nullable=False)
    event_type = Column(Enum(EventEnum))
    result = Column(Boolean, nullable=False)

    def __init__(self, user_name: str, time: datetime, browser: str, event_type: enum, result: bool) -> None:
        self.user_name = user_name
        self.time = time
        self.browser = browser
        self.event_type = event_type
        self.result = result

    def __repr__(self) -> str:
        return f'<User {self.user_name}>'

import uuid
from datetime import datetime
import enum
from sqlalchemy import Boolean, Column, DateTime, String, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"))

    def __init__(self, login: str, password: str, first_name: str, last_name: str, role_id: UUID, is_admin: bool = False) -> None:
        self.is_admin = is_admin
        self.login = login
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name
        self.role_id = role_id

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'

class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    lvl = Column(Integer(), default=0, unique=True, nullable=False)
    name_role = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    max_year = Column(Integer(), default=1980, nullable=False)

    def __init__(self, lvl: int, name_role: str, description: str, max_year: int) -> None:
        self.lvl = lvl
        self.name_role = name_role
        self.description = description
        self.max_year = max_year

    def __repr__(self) -> str:
        return f'<{self.name_role}:{self.lvl}>'


class EventEnum(enum.Enum):
    login = "login"
    logout = "logout"
    refresh = "refresh"


class History(Base):
    __tablename__ = 'login_history'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    time = Column(DateTime, default=datetime.utcnow)
    browser = Column(String(255), nullable=False)
    event_type = Column(Enum(EventEnum))
    result = Column(Boolean, nullable=False)

    def __init__(self, user_id: UUID, time: datetime, browser: str, event_type: enum, result: bool) -> None:
        self.user_id = user_id
        self.time = time
        self.browser = browser
        self.event_type = event_type
        self.result = result

    def __repr__(self) -> str:
        return f'<User {self.user_id}>'

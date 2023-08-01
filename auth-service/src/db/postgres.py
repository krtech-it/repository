from core.config import app_settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

Base = declarative_base()

engine = create_async_engine(url=app_settings.database_dsn(), echo=True, future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def command_create_role(repository, model, data) -> None:
    async with async_session() as session:
        repository_obj = repository(session=session)
        role = await repository_obj.get_obj_by_attr_name(model=model, attr_name='lvl', attr_value=data['lvl'])
        if role is None:
            await repository_obj.create_obj(model, data)


async def command_create_user(repository, model_user, model_role, data) -> str:
    async with async_session() as session:
        repository_obj = repository(session=session)

        role = await repository_obj.get_first_obj_order_by_attr_name(model_role, 'lvl')
        if role is None:
            return 'Default role is not exists.\n try command -- python3 cli.py create_default_role'

        user = await repository_obj.get_obj_by_attr_name(model=model_user, attr_name='login', attr_value=data['login'])
        if user is None:
            data['role_id'] = role.id
            await repository_obj.create_obj(model_user, data)
            return 'Done!'

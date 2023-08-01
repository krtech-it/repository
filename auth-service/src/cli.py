import typer
import asyncio

from db.postgres import command_create_role, command_create_user
from models.entity import Role, User
from services.repository import BaseRepository

app = typer.Typer()


@app.command(name='create_default_role')
def create_default_role(
        name: str = "standart",
        level: int = 0,
        max_year: int = 1980
):
    data = {
        'lvl': level,
        'name_role': name,
        'description': '',
        'max_year': max_year
    }
    asyncio.run(command_create_role(BaseRepository, Role, data))
    print('Done!')


@app.command(name='create_superuser')
def create_superuser(
        login: str = 'admin',
        password: str = 'admin',
        first_name: str = 'admin',
        last_name: str = 'admin',
        email: str = 'test@test.ru'
):
    data = {
        'is_admin': True,
        'login': login,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
    }
    result = asyncio.run(command_create_user(BaseRepository, User, Role, data))
    print(result)


if __name__ == "__main__":
    app()

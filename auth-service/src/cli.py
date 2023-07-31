import typer
import asyncio

from db.postgres import create_role
from models.entity import Role


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
    asyncio.run(create_role(Role, data))
    print('Done!')


if __name__ == "__main__":
    app()

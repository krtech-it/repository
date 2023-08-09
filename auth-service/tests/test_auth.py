import pytest
from httpx import AsyncClient
from http import HTTPStatus
import itertools

from models.entity import User, Role
from uuid import uuid4

START_URL = "/api/v1/auth/"


@pytest.mark.parametrize(
    'query_data, expected_answer, mock_get_user',
    [
        (
                {'login': 'admin', 'password': 'admin'},
                {'status': HTTPStatus.OK, 'response_body': None},
                User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(), email='test@mail.ru', is_admin=False)
        ),
        (
                {'login': 'admin', 'password': 'admin'},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Пользователя не существует"}},
                None
        ),
        (
                {'login': 'admin', 'password': 'admin2'},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Неверный пароль"}},
                User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(), email='test@mail.ru', is_admin=False)
        )
    ]
)
async def test_login(query_data, expected_answer, mock_get_user, ac: AsyncClient, monkeypatch):
    async def mock_get_obj_by_attr_name(*args, **kwargs):
        return mock_get_user

    async def mock_return_null(*args, **kwargs):
        return None

    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_attr_name', mock_get_obj_by_attr_name)
    monkeypatch.setattr('services.user.BaseRepository.create_obj', mock_return_null)
    monkeypatch.setattr('services.user.CacheRedis._put_object_to_cache', mock_return_null)

    response = await ac.post(START_URL + "login/", json=query_data)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'query_data, expected_answer, mock_get_users, mock_get_role',
    [
        (
                {"login": "admin", "password": "stringst", "first_name": "string", "last_name": "string", "email": "test@test.ru"},
                {'status': HTTPStatus.OK, 'response_body': None},
                tuple(),
                [None, Role(lvl=0, name_role="str", description="str", max_year="int")]
        ),
        (
                {"login": "admin", "password": "stringst", "first_name": "string", "last_name": "string", "email": "test@test.ru"},
                {'status': HTTPStatus.OK, 'response_body': None},
                tuple(),
                [Role(lvl=0, name_role="str", description="str", max_year="int")]
        ),
        (
                {"login": "admin", "password": "stringst", "first_name": "string", "last_name": "string",
                 "email": "test@test.ru"},
                {'status': HTTPStatus.BAD_REQUEST,
                 'response_body': {"detail": "Пользователь с таким login уже существует"}},
                 (User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                       email='test@mail.ru', is_admin=False),),
                [Role(lvl=0, name_role="str", description="str", max_year="int")]
        ),
        (
                {"login": "admin", "password": "stringst", "first_name": "string", "last_name": "string",
                 "email": "test@test.ru"},
                {'status': HTTPStatus.BAD_REQUEST,
                 'response_body': {"detail": "Пользователь с таким email уже существует"}},
                 (User(login='user', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                       email='test@test.ru', is_admin=False),),
                [Role(lvl=0, name_role="str", description="str", max_year="int")]
        )
        # (
        #         {'login': 'admin', 'password': 'admin'},
        #         {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Пользователя не существует"}},
        #         None
        # ),
        # (
        #         {'login': 'admin', 'password': 'admin2'},
        #         {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Неверный пароль"}},
        #         User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(), email='test@mail.ru', is_admin=False)
        # )
    ]
)
async def test_sign_up(query_data, expected_answer, mock_get_users, mock_get_role, ac: AsyncClient, monkeypatch):
    x = 0
    async def mock_get_list_obj_by_list_attr_name_operator_or(*args, **kwargs):
        return itertools.chain(mock_get_users)

    async def mock_return_null(*args, **kwargs):
        return None

    async def mock_get_first_obj_order_by_attr_name(*args, **kwargs):
        nonlocal x
        if x == 0:
            x+=1
            return mock_get_role[0]
        else:
            role = mock_get_role[1]
            role.id = uuid4()
            return role

    monkeypatch.setattr('services.user.BaseRepository.get_list_obj_by_list_attr_name_operator_or',
                        mock_get_list_obj_by_list_attr_name_operator_or)
    monkeypatch.setattr('services.user.BaseRepository.get_first_obj_order_by_attr_name',
                        mock_get_first_obj_order_by_attr_name)
    monkeypatch.setattr('services.user.BaseRepository.create_obj', mock_return_null)

    response = await ac.post(START_URL + "sign_up/", json=query_data)
    assert response.status_code == expected_answer['status']
    # assert response.status_code == expected_answer['status']


import time

import pytest
from httpx import AsyncClient
from http import HTTPStatus
import itertools
from async_fastapi_jwt_auth import AuthJWT

from models.entity import User, Role
from uuid import uuid4

from schemas.entity import FieldFilter
from services.auth_jwt import BaseAuthJWT

START_URL = "/api/v1/auth/"
TIME_ACCESS_TOKEN = 25


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
    ]
)
async def test_sign_up(query_data, expected_answer, mock_get_users, mock_get_role, ac: AsyncClient, monkeypatch):
    count = 0

    async def mock_get_list_obj_by_list_attr_name_operator_or(*args, **kwargs):
        assert args[1] == [
            {
                'model': User,
                'fields': [
                    FieldFilter(attr_name='login', attr_value=query_data['login']),
                    FieldFilter(attr_name='email', attr_value=query_data['email'])
                ]
            },
        ]
        return itertools.chain(mock_get_users)

    async def mock_return_null(*args, **kwargs):
        return None

    async def mock_get_first_obj_order_by_attr_name(*args, **kwargs):
        nonlocal count
        if count == 0:
            count+=1
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
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'input_headers, expected_answer, mock_check_access, mock_get_cache',
    [
        (
                {},
                {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'response_body': {"detail": 'Signature has expired'}},
                {'jti': str(uuid4())},
                True
        ),
        (
                {'User-Agent': 'yandex'},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {'detail': 'подозрение на небезопасный вход'}},
                {'jti': str(uuid4()), 'user_agent': 'google', 'exp': TIME_ACCESS_TOKEN + int(time.time())},
                False
        ),
        (
                {'User-Agent': 'google'},
                {'status': HTTPStatus.OK, 'response_body': {'jti': 'jti', 'user_agent': 'google', 'exp': TIME_ACCESS_TOKEN + int(time.time())}},
                {'jti': str(uuid4()), 'user_agent': 'google', 'exp': TIME_ACCESS_TOKEN + int(time.time())},
                False
        )
    ]
)
async def test_get_user(input_headers, expected_answer, mock_check_access, mock_get_cache, ac: AsyncClient, monkeypatch):
    if expected_answer['response_body'].get('jti'):
        expected_answer['response_body']['jti'] = mock_check_access['jti']

    async def mock_check_access_token(*args, **kwargs):
        return mock_check_access

    async def mock_object_from_cache(*args, **kwargs):
        return mock_get_cache

    async def mock_put_object_to_cache(self, obj, time_cache):
        assert time_cache <= TIME_ACCESS_TOKEN
        return None

    monkeypatch.setattr('services.auth_jwt.BaseAuthJWT.check_access_token', mock_check_access_token)
    monkeypatch.setattr('services.redis_cache.CacheRedis._object_from_cache', mock_object_from_cache)
    monkeypatch.setattr('services.redis_cache.CacheRedis._put_object_to_cache', mock_put_object_to_cache)

    response = await ac.get(START_URL + "get_user/", headers=input_headers)
    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'user, expected_answer, input_headers, settings_test',
    [
        (
            User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                 email='test@mail.ru', is_admin=False),
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'response_body': {"detail": 'Signature has expired'}},
            {'User-Agent': 'google'},
            {'mock_get_cache': False, 'user_agent_token': 'google'}
        ),
        (
            User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                 email='test@mail.ru', is_admin=False),
            {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": 'подозрение на небезопасный вход'}},
            {'User-Agent': 'google2'},
            {'mock_get_cache': True, 'user_agent_token': 'google'}
        ),
        (
            User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                 email='test@mail.ru', is_admin=False),
            {'status': HTTPStatus.UNPROCESSABLE_ENTITY, 'response_body': {"detail": 'access токен не принадлежит refresh токену'}},
            {'User-Agent': 'google'},
            {'mock_get_cache': True, 'user_agent_token': 'google', 'fake_access': True}
        ),
        (
            User(login='admin', password='admin', first_name='dima', last_name='ivanov', role_id=uuid4(),
                 email='test@mail.ru', is_admin=False),
            {'status': HTTPStatus.OK, 'response_body': None},
            {'User-Agent': 'google'},
            {'mock_get_cache': True, 'user_agent_token': 'google'}
        )
    ]
)
async def test_refresh(user, expected_answer, input_headers, settings_test, ac: AsyncClient, monkeypatch):
    async def mock_object_from_cache(*args, **kwargs):
        return settings_test['mock_get_cache']

    async def mock_return_null(*args, **kwargs):
        return None

    monkeypatch.setattr('services.redis_cache.CacheRedis._object_from_cache', mock_object_from_cache)
    monkeypatch.setattr('services.redis_cache.CacheRedis._delete_object_from_cache', mock_return_null)
    monkeypatch.setattr('services.redis_cache.CacheRedis._put_object_to_cache', mock_return_null)
    monkeypatch.setattr('services.user.BaseRepository.create_obj', mock_return_null)

    user.id = uuid4()
    user_claims = {
            'user_agent': settings_test['user_agent_token'],
            'is_admin': user.is_admin
    }
    access_token = await AuthJWT().create_access_token(
        subject=str(user.id), user_claims=user_claims
    )
    if settings_test.get('fake_access'):
        uuid_access = 'hjkfghfhj'
    else:
        uuid_access = access_token.split('.')[-1]
    user_claims['uuid_access'] = uuid_access
    refresh_token = await AuthJWT().create_refresh_token(
        subject=str(user.id), user_claims=user_claims
    )

    response = await ac.post(
        START_URL + "refresh/",
        headers=input_headers,
        cookies={'access_token_cookie': access_token, 'refresh_token_cookie': refresh_token}
    )

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']

    ac.cookies.clear()

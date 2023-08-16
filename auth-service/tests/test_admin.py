import pytest
from httpx import AsyncClient
from http import HTTPStatus

from models.entity import User, Role
from uuid import uuid4


START_URL = "/api/v1/admin/"

# данные для тестов
role_dict = {
    'lvl': 1,
    'name_role': 'subscribed',
    'description': '',
    'max_year': 1900
}
role_with_certain_id = Role(**role_dict)
role_id = str(uuid4())
role_with_certain_id.id = role_id

user_dict = {
    'login': 'admin',
    'password': 'admin',
    'first_name': 'dima',
    'last_name': 'ivanov',
    'role_id': role_id,
    'email': 'test@mail.ru',
    'is_admin': False
}
user_id = str(uuid4())
user_with_certain_id = User(**user_dict)
user_with_certain_id.id = user_id

role_user_dict = {
    'user_id': user_id,
    'role_id': role_id
}


@pytest.mark.parametrize(
    'query_data, expected_answer, mock_get_role',
    [
        (
                role_dict,
                {'status': HTTPStatus.OK, 'response_body': role_dict},
                None
        ),
        (
                role_dict,
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Такая роль уже существует"}},
                Role(**role_dict)
        )
    ]
)
async def test_create(query_data, expected_answer, mock_get_role, ac: AsyncClient, monkeypatch):
    count = 0

    async def mock_get_obj_by_attr_name(*args, **kwargs):
        return mock_get_role

    async def mock_return_null(*args, **kwargs):
        return None

    async def mock_get_info_from_access_token(*args, **kwargs):
        return {'is_admin': True}

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_get_info_from_access_token)
    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_attr_name', mock_get_obj_by_attr_name)
    monkeypatch.setattr('services.user.BaseRepository.create_obj', mock_return_null)

    response = await ac.patch(START_URL + "create/", headers={'User-Agent': 'google'}, json=query_data)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'query_data, expected_answer, mock_get_role, role_id',
    [
        (
                role_dict,
                {'status': HTTPStatus.OK, 'response_body': role_dict},
                role_with_certain_id,
                role_id
        ),
        (
                role_dict,
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Такой роли не существует"}},
                None,
                str(uuid4())
        )
    ]
)
async def test_update(query_data, expected_answer, mock_get_role, role_id, ac: AsyncClient, monkeypatch):
    async def mock_get_obj_by_attr_name(*args, **kwargs):
        return mock_get_role

    async def mock_get_info_from_access_token(*args, **kwargs):
        return {'is_admin': True}

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_get_info_from_access_token)
    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_attr_name', mock_get_obj_by_attr_name)

    response = await ac.patch(START_URL + f"update/{role_id}/", headers={'User-Agent': 'google'}, json=query_data)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'query_data, expected_answer, mock_get_role, mock_get_user',
    [
        (
                role_user_dict,
                {'status': HTTPStatus.OK, 'response_body': 'role assigned'},
                role_with_certain_id,
                user_with_certain_id,
        ),
        (
                role_user_dict,
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Такой роли не существует"}},
                None,
                user_with_certain_id,
        ),
        (
                role_user_dict,
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": "Такого пользователя не существует"}},
                role_with_certain_id,
                None
        )
    ]
)
async def test_assign(query_data, expected_answer, mock_get_role, mock_get_user, ac: AsyncClient, monkeypatch):
    async def mock_get_obj_by_attr_name(*args, **kwargs):
        return mock_get_role

    async def mock_get_obj_by_pk(*args, ** kwargs):
        return mock_get_user

    async def mock_get_info_from_access_token(*args, **kwargs):
        return {'is_admin': True}

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_get_info_from_access_token)
    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_attr_name', mock_get_obj_by_attr_name)
    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_pk', mock_get_obj_by_pk)

    response = await ac.post(START_URL + "assign/", headers={'User-Agent': 'google'}, json=query_data)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']

import pytest
from httpx import AsyncClient
from http import HTTPStatus

from models.entity import User
from uuid import uuid4

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
async def test_add_specific_operations(query_data, expected_answer, mock_get_user, ac: AsyncClient, monkeypatch):
    async def mock_get_obj_by_attr_name(*args, **kwargs):
        return mock_get_user

    async def mock_return_null(*args, **kwargs):
        return None

    monkeypatch.setattr('services.user.BaseRepository.get_obj_by_attr_name', mock_get_obj_by_attr_name)
    monkeypatch.setattr('services.user.BaseRepository.create_obj', mock_return_null)
    monkeypatch.setattr('services.user.CacheRedis._put_object_to_cache', mock_return_null)

    response = await ac.post("/api/v1/auth/login/", json=query_data)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']

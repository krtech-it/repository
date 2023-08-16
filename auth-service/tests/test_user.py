import pytest
from httpx import AsyncClient
from http import HTTPStatus

from models.entity import User, Role
from uuid import uuid4

from core.config import ErrorName
from schemas.entity import UserProfil
from werkzeug.security import check_password_hash, generate_password_hash

START_URL = "/api/v1/profil/"


@pytest.mark.parametrize(
    'role_data, user_data, expected_answer,',
    [
        (
                {"lvl": 0, "admin_role": "advanced", "description": "some description", "max_year": 2022},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': {}},
        ),
        (
                {"lvl": 1, "role1": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": True},
                {'status': HTTPStatus.OK, 'response_body': {}},
        ),
    ]
        
    )
async def test_get_user_data(role_data, user_data, expected_answer, ac: AsyncClient, monkeypatch):
    async def mock_info_from_access_token(*args, **kwargs):
        return {"sub": str(uuid4())}
    
    async def mock_get_obj_by_pk(*args, **kwargs):
        return User(
            login=user_data.get("login"),
            password=user_data.get("password"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            role_id=user_data.get("role_id"),
            email=user_data.get("email"),
            is_admin=user_data.get("is_admin")
        )
    
    async def mock_get_role(*args, **kwargs):
        return Role(
            lvl=role_data.get("lvl"),
            name_role=role_data.get("name_role"),
            description=role_data.get("description"),
            max_year=role_data.get("max_year"),
        )
    
    user_answer = UserProfil(
        login=user_data.get("login"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
        name_role=f"{role_data.get('lvl')}:{role_data.get('name_role')}",
        email=user_data.get("email")
    )

    expected_answer["response_body"] = user_answer.model_dump()

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_info_from_access_token)
    monkeypatch.setattr('services.repository.BaseRepository.get_obj_by_pk', mock_get_obj_by_pk)
    monkeypatch.setattr('services.role.BaseRole.get_role', mock_get_role)

    response = await ac.get(START_URL + "self_data/")

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'change_profil, role_data, user_data, expected_answer, duplicat_error',
    [
        (
                {"login": "new_test_login"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': {}},
                None
        ),
        (
                {"login": "new_test_login", "first_name": "new_first_name"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': {}},
                None
        ),
        (
                {"last_name": "new_last_name"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': {}},
                None
        ),
        (
                {"login": "new_test_login"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail":'Пользователь с таким login уже существует'}},
                ErrorName.LoginAlreadyExists
        ),
        (
                {"email": "new_email1@mail.com"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail":'Пользователь с таким email уже существует'}},
                ErrorName.EmailAlreadyExists
        ),
        (
                {"email": "new_e31mail1@mail1.com"},
                {"lvl": 1, "name_role": "advanced", "description": "some description", "max_year": 2020},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': {}},
                None
        ),
    ]
        
    )
async def test_change_profile_user(change_profil, role_data, user_data, expected_answer, duplicat_error: None | str, ac: AsyncClient, monkeypatch):
    async def mock_info_from_access_token(*args, **kwargs):
        return {"sub": str(uuid4())}
    
    async def mock_get_obj_by_pk(*args, **kwargs):
        return User(
            login=user_data.get("login"),
            password=user_data.get("password"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            role_id=user_data.get("role_id"),
            email=user_data.get("email"),
            is_admin=user_data.get("is_admin")
        )
    
    async def mock_get_role(*args, **kwargs):
        return Role(
            lvl=role_data.get("lvl"),
            name_role=role_data.get("name_role"),
            description=role_data.get("description"),
            max_year=role_data.get("max_year"),
        )
    

    async def mock_search_for_duplicates(*args, **kwargs) -> None | str:
        return duplicat_error
    
    user_answer = UserProfil(
        login=change_profil.get("login") if change_profil.get("login") else user_data.get("login"),
        first_name=change_profil.get("first_name") if change_profil.get("first_name") else user_data.get("first_name"),
        last_name=change_profil.get("last_name") if change_profil.get("last_name") else user_data.get("last_name"),
        name_role=f"{role_data.get('lvl')}:{role_data.get('name_role')}",
        email=change_profil.get("email") if change_profil.get("email") else user_data.get("email")
    )

    if duplicat_error is None:
        expected_answer["response_body"] = user_answer.model_dump()

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_info_from_access_token)
    monkeypatch.setattr('services.repository.BaseRepository.get_obj_by_pk', mock_get_obj_by_pk)
    monkeypatch.setattr('services.role.BaseRole.get_role', mock_get_role)
    monkeypatch.setattr('services.user.UserManage.search_for_duplicates', mock_search_for_duplicates)

    response = await ac.patch(START_URL + "self_data/", json=change_profil)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']


@pytest.mark.parametrize(
    'change_password , user_data, expected_answer,',
    [
        (
                {"old_password": "test1234", "new_password": "123434ffr"},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.OK, 'response_body': "password changed"},
        ),
        (
                {"old_password": "test123433", "new_password": "123434ffr"},
                {"login": "test1234", "password": "test1234", "first_name": "first_name", "last_name": "last_name", "role_id": uuid4(), "email": "testmail@mail.com", "is_admin": False},
                {'status': HTTPStatus.BAD_REQUEST, 'response_body': {"detail": 'Неверный пароль'}},
        ),
    ])
async def test_change_password(change_password, user_data, expected_answer, ac: AsyncClient, monkeypatch):
    async def mock_info_from_access_token(*args, **kwargs):
        return {"sub": str(uuid4())}

    async def mock_get_obj_by_pk(*args, **kwargs):
        return User(
            login=user_data.get("login"),
            password=user_data.get("password"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name"),
            role_id=user_data.get("role_id"),
            email=user_data.get("email"),
            is_admin=user_data.get("is_admin")
        )

    def mock_check_password(*args, **kwargs):
        hash_password = generate_password_hash(user_data.get("password"))
        return check_password_hash(hash_password, change_password.get("old_password"))

    monkeypatch.setattr('services.user.BaseAuth.get_info_from_access_token', mock_info_from_access_token)
    monkeypatch.setattr('services.repository.BaseRepository.get_obj_by_pk', mock_get_obj_by_pk)
    monkeypatch.setattr('models.entity.User.check_password', mock_check_password)

    response = await ac.post(START_URL + "change_password/", json=change_password)

    assert response.status_code == expected_answer['status']
    assert response.json() == expected_answer['response_body']

import pytest
import httpx

from infra.db.models.users import User
from infra.db.repository.user_repo import UserRepository
from api.schemas.users_schemas import UserViewSchema
from infra.security.jwt import decode


pytest_mark_asyncio = pytest.mark.asyncio
urls = {
    'profile': {
        'login': '/api/profile/login',
        'logout': '/api/profile/logout',
        'registration': '/api/profile/registration'
    },
    'user_api': {
        'get_users': '/api/users',
        'create_user': '/api/users',
        'get_user': '/api/users/{}',
        'update_user': '/api/users/{}',
        'delete_user': '/api/users/{}'

    },
    'groups_api': {
        'get_groups': '/api/groups',
        'add_users': '/api/groups/{}/add_users',
        'exclude_users': '/api/groups/{}/exclude_users'
    }
}


@pytest_mark_asyncio
async def test_registration(simple_client: httpx.AsyncClient, user_repo: UserRepository):
    data = {
        'tg_name': 'new_tg',
        'email': 'user@mail.ru',
        'password': 'test-password'
    }
    response = await simple_client.post(urls['profile']['registration'], json=data)
    assert response.status_code == 200
    registered = await user_repo.get_user_by_email(data['email'])
    assert registered is not None
    expected = UserViewSchema.model_validate(
        registered, from_attributes=True).model_dump()
    assert response.json() == expected


@pytest_mark_asyncio
async def test_registration_fail(simple_client: httpx.AsyncClient):
    data = {}
    response = await simple_client.post(urls['profile']['registration'], json=data)
    assert response.status_code == 422
    assert response.json() == {
        'detail': [
            {
                'type': 'missing',
                'loc': ['body', 'tg_name'],
                'msg': 'Field required',
                'input': {}
            },
            {
                'type': 'missing',
                'loc': ['body', 'email'],
                'msg': 'Field required',
                'input': {}
            },
            {
                'type': 'missing',
                'loc': ['body', 'password'],
                'msg': 'Field required',
                'input': {}
            }
        ]
    }


@pytest_mark_asyncio
async def test_login(client: httpx.AsyncClient, simple_user: User):
    response = await client.post(urls['profile']['login'], json={'email': simple_user.email, 'password': 'test_password'})
    assert response.status_code == 200
    assert response.json() == {'detail': 'logged in'}
    token = client.cookies.get('token', None)
    assert token is not None
    payload = decode(token)
    assert payload['user_id'] == simple_user.id


@pytest_mark_asyncio
async def test_login_fail_pas(client: httpx.AsyncClient, simple_user: User):
    data = {
        'email': simple_user.email,
        'password': 'test_passwor'
    }
    response = await client.post(urls['profile']['login'], json=data)
    assert response.status_code == 400
    assert response.json() == {'detail': {
        'service': 'UserAuthService', 'msgs': ['Wrong password']}}


@pytest_mark_asyncio
async def test_login_fail_email(client: httpx.AsyncClient):
    data = {
        'email': 'dasdasd',
        'password': 'test_password'
    }
    response = await client.post(urls['profile']['login'], json=data)
    assert response.status_code == 400
    assert response.json() == {'detail': {'service': 'UserAuthService', 'msgs': [
        f'Unable to find user with email ({data["email"]})']}}


@pytest_mark_asyncio
async def test_logout(simple_client: httpx.AsyncClient):
    response = await simple_client.post(urls['profile']['logout'])
    assert response.status_code == 200
    assert response.json() == {
        'detail': 'logged out'
    }
    token = simple_client.cookies.get('token', None)
    assert token is None


@pytest_mark_asyncio
async def test_logout_fail(client: httpx.AsyncClient):
    response = await client.post(urls['profile']['logout'])
    assert response.status_code == 401
    assert response.json() == {
        'detail': {
            'error': 'token was not provide'
        }
    }

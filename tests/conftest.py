import pytest
from starlette.testclient import TestClient

import tests.testutils as testutils
from main import app
import apps.core.users.implementation as impl_users
import apps.core.users.models as models_users


@pytest.fixture(scope="session")
def client() -> TestClient:
    client = TestClient(app)
    yield client


@pytest.fixture(scope='session')
def admin_user() -> models_users.UserPost:
    user = testutils.random_user_post(admin=True, disabled=False)
    new_user = impl_users.impl_post_user(user)
    yield user
    impl_users.impl_delete_user_from_db(new_user.id)


@pytest.fixture(scope='session')
def admin_headers(client, admin_user):
    data = {
        "username": admin_user.username,
        "password": admin_user.password
    }
    res = client.post('/api/core/auth/token', data)

    assert res.status_code == 200
    return {
        "Authorization": f'Bearer {res.json()["access_token"]}'
    }

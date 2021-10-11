import apps.core.users.implementation as users_impl
import tests.testutils as testutils


def test_get_projects_unauthenticated(client):
    # Act
    res = client.get('/api/core/projects/?segment_length=10&index=0')
    # assert
    assert res.status_code == 401


def test_get_projects(client, std_headers):
    # Act
    res = client.get('/api/core/projects/?segment_length=10&index=0', headers=std_headers)
    # Assert
    assert res.status_code == 200


def test_get_all_projects(client, std_headers):
    # Act
    res = client.get('/api/core/projects/all?segment_length=10&index=0', headers=std_headers)
    # Assert
    assert res.status_code == 401


def test_get_all_projects_as_admin(client, admin_headers):
    # Act
    res = client.get('/api/core/projects/all?segment_length=10&index=0', headers=admin_headers)
    # Assert
    assert res.status_code == 200

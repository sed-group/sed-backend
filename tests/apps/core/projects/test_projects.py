import random as r

import apps.core.users.implementation as users_impl
import apps.core.projects.implementation as impl
import tests.apps.core.projects.testutils as tu_projects


def test_get_projects_unauthenticated(client):
    # Act
    res = client.get('/api/core/projects/?segment_length=10&index=0')
    # assert
    assert res.status_code == 401


def test_get_projects(client, std_headers, std_user):
    # Setup
    max_projects = 30
    current_user = users_impl.impl_get_user_with_username(std_user.username)
    seeded_projects = tu_projects.seed_random_projects(current_user.id, amount=r.randint(5, max_projects))
    # Act
    res = client.get(f'/api/core/projects/?segment_length={max_projects}&index=0', headers=std_headers)
    # Assert
    assert res.status_code == 200
    assert len(res.json()) == len(seeded_projects)
    # Cleanup
    tu_projects.delete_projects(seeded_projects)


def test_get_all_projects(client, std_headers):
    # Act
    res = client.get('/api/core/projects/all?segment_length=10&index=0', headers=std_headers)
    # Assert
    assert res.status_code == 403


def test_get_all_projects_as_admin(client, admin_headers, admin_user):
    # Setup
    max_projects = 30
    current_user = users_impl.impl_get_user_with_username(admin_user.username)
    seeded_projects = tu_projects.seed_random_projects(current_user.id, amount=r.randint(5, max_projects))
    amount_of_projects = len(impl.impl_get_projects())
    # Act
    res = client.get('/api/core/projects/all', headers=admin_headers)
    # Assert
    assert res.status_code == 200
    assert amount_of_projects == len(res.json())
    # Cleanup
    tu_projects.delete_projects(seeded_projects)

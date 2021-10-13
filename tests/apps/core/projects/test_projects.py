import random as r

import apps.core.users.implementation as impl_users
import apps.core.projects.implementation as impl
import tests.apps.core.projects.testutils as tu_projects
import tests.apps.core.users.testutils as tu_users
import apps.core.projects.models as models


def test_get_projects_unauthenticated(client):
    # Act
    res = client.get('/api/core/projects/?segment_length=10&index=0')
    # assert
    assert res.status_code == 401


def test_get_projects(client, std_headers, std_user):
    # Setup
    max_projects = 30
    current_user = impl_users.impl_get_user_with_username(std_user.username)
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
    current_user = impl_users.impl_get_user_with_username(admin_user.username)
    seeded_projects = tu_projects.seed_random_projects(current_user.id, amount=r.randint(5, max_projects))
    amount_of_projects = len(impl.impl_get_projects())
    # Act
    res = client.get('/api/core/projects/all', headers=admin_headers)
    # Assert
    assert res.status_code == 200
    assert amount_of_projects == len(res.json())
    # Cleanup
    tu_projects.delete_projects(seeded_projects)


def test_get_project_as_owner(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id)
    # Act
    res = client.get(f'/api/core/projects/{p.id}', headers=std_headers)
    fetched_project = models.Project(**res.json())

    found_owner = False
    for user in fetched_project.participants:
        if user.id == current_user.id:
            found_owner = True
    # Assert
    assert res.status_code == 200
    assert fetched_project.id == p.id
    assert fetched_project.name == p.name
    assert found_owner is True


def test_get_project_as_participant(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)
    participants = {
        current_user.id: models.AccessLevel.EDITOR
    }
    p = tu_projects.seed_random_project(owner_user.id, participants=participants)
    # Act
    res = client.get(f'/api/core/projects/{p.id}', headers=std_headers)
    project = models.Project(**res.json())
    participants_id_list = []
    for participant in project.participants:
        participants_id_list.append(participant.id
                                    )
    # Assert
    assert res.status_code == 200
    assert project.id == p.id
    assert owner_user.id in participants_id_list
    assert project.participants_access[owner_user.id] == models.AccessLevel.OWNER
    assert current_user.id in participants_id_list
    assert project.participants_access[current_user.id] == models.AccessLevel.EDITOR
    # Cleanup
    impl_users.impl_delete_user_from_db(owner_user.id)
    impl.impl_delete_project(project.id)


def test_get_project_as_nonparticipant(client, std_headers):
    # Setup
    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)
    p = tu_projects.seed_random_project(owner_user.id)
    # Act
    res = client.get(f'/api/core/projects/{p.id}', headers=std_headers)
    # Assert
    assert res.status_code == 403
    # Cleanup
    impl.impl_delete_project(p.id)
    impl_users.impl_delete_user_from_db(owner_user.id)


def test_delete_project_as_owner(client, std_headers):
    pass


def test_delete_project_as_nonadmin(client, std_headers):
    pass

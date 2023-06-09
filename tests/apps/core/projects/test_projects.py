import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.core.projects.implementation as impl
import tests.testutils as tu
import tests.apps.core.projects.testutils as tu_projects
import tests.apps.core.users.testutils as tu_users
import sedbackend.apps.core.projects.models as models


def test_get_projects_unauthenticated(client):
    # Act
    res = client.get('/api/core/projects?segment_length=10&index=0')
    # assert
    assert res.status_code == 401


def test_get_projects(client, std_headers, std_user):
    # Setup
    max_projects = 30
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    seeded_projects = tu_projects.seed_random_projects(current_user.id, amount=r.randint(5, max_projects))
    # Act
    res = client.get(f'/api/core/projects?segment_length={max_projects}&index=0', headers=std_headers)
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
    amount_of_projects = len(impl.impl_get_projects(current_user.id))
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
    # Cleanup
    tu_projects.delete_projects([p])


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


def test_delete_project_as_non_admin(client, std_headers, std_user):
    # Setup
    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(owner_user.id, participants={
        current_user.id: models.AccessLevel.EDITOR
    })
    # Act
    res = client.delete(f'/api/core/projects/{p.id}', headers=std_headers)
    res2 = client.get(f'/api/core/projects/{p.id}', headers=std_headers)
    # Assert
    assert res.status_code == 403
    assert res2.status_code == 200
    # Cleanup
    impl.impl_delete_project(p.id)
    impl_users.impl_delete_user_from_db(owner_user.id)


def test_delete_project_as_admin(client, std_headers, std_user):
    # Setup
    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(owner_user.id, participants={
        current_user.id: models.AccessLevel.ADMIN
    })
    # Act
    res = client.delete(f'/api/core/projects/{p.id}', headers=std_headers)
    res2 = client.get(f'/api/core/projects/{p.id}', headers=std_headers)
    # Assert
    assert res.status_code == 200
    with pytest.raises(HTTPException):
        impl.impl_get_project(p.id)
    assert res2.status_code == 404
    # Cleanup
    impl_users.impl_delete_user_from_db(owner_user.id)


def test_delete_project_as_unauthenticated(client):
    # Setup
    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)
    p = tu_projects.seed_random_project(owner_user.id)
    # Act
    res = client.delete(f'/api/core/projects/{p.id}')
    # Assert
    assert res.status_code == 401
    project = impl.impl_get_project(p.id)
    assert project is not None
    assert project.id == p.id
    # Cleanup
    impl.impl_delete_project(p.id)
    impl_users.impl_delete_user_from_db(owner_user.id)


def test_add_participant_as_admin(client, std_headers, std_user):
    # Setup
    participant_user_post = tu_users.random_user_post(admin=False, disabled=False)
    participant_user = impl_users.impl_post_user(participant_user_post)
    owner_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(owner_user.id)
    access_level = models.AccessLevel.EDITOR
    # Act
    res = client.post(f'/api/core/projects/{p.id}/participants'
                      f'?user_id={participant_user.id}'
                      f'&access_level={access_level.value}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    participant_id_list = []
    for participant in p_updated.participants:
        participant_id_list.append(participant.id)
    # Assert
    assert res.status_code == 200
    assert participant_user.id in participant_id_list
    assert p_updated.participants_access[participant_user.id] == access_level
    # Cleanup
    impl_users.impl_delete_user_from_db(participant_user.id)
    impl.impl_delete_project(p.id)


def test_add_participant_as_non_admin(client, std_headers, std_user):
    # Setup
    participant_user_post = tu_users.random_user_post(admin=False, disabled=False)
    participant_user = impl_users.impl_post_user(participant_user_post)

    owner_user_post = tu_users.random_user_post(admin=False, disabled=False)
    owner_user = impl_users.impl_post_user(owner_user_post)

    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(owner_user.id, participants={
        current_user.id: models.AccessLevel.EDITOR
    })
    access_level = models.AccessLevel.EDITOR
    # Act
    res = client.post(f'/api/core/projects/{p.id}/participants'
                      f'?user_id={participant_user.id}'
                      f'&access_level={access_level.value}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    participant_id_list = []
    for participant in p_updated.participants:
        participant_id_list.append(participant.id)
    # Assert
    assert res.status_code == 403
    assert participant_user.id not in participant_id_list
    assert participant_user.id not in p_updated.participants_access
    # Cleanup
    impl_users.impl_delete_user_from_db(participant_user.id)
    impl_users.impl_delete_user_from_db(owner_user.id)
    impl.impl_delete_project(p.id)


def test_remove_participant_as_admin(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    participant_user = tu_users.seed_random_user(admin=False, disabled=False)
    p = tu_projects.seed_random_project(current_user.id, participants={participant_user.id: models.AccessLevel.EDITOR})
    # Act
    res = client.delete(f'/api/core/projects/{p.id}/participants/{participant_user.id}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    participant_id_list = []
    for participant in p_updated.participants:
        participant_id_list.append(participant.id)
    # Assert
    assert res.status_code == 200
    assert participant_user.id not in p_updated.participants_access
    assert participant_user.id not in participant_id_list
    # Cleanup
    impl_users.impl_delete_user_from_db(participant_user.id)
    impl.impl_delete_project(p.id)


def test_remove_participant_as_non_admin(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    owner_user = tu_users.seed_random_user(admin=False, disabled=False)
    participant_user = tu_users.seed_random_user(admin=False, disabled=False)
    p = tu_projects.seed_random_project(owner_user.id,
                                        participants={
                                            participant_user.id: models.AccessLevel.EDITOR,
                                            current_user.id: models.AccessLevel.EDITOR
                                        })
    # Act
    res = client.delete(f'/api/core/projects/{p.id}/participants/{participant_user.id}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    participant_id_list = []
    for participant in p_updated.participants:
        participant_id_list.append(participant.id)
    # Assert
    assert res.status_code == 403
    assert participant_user.id in p_updated.participants_access
    assert participant_user.id in participant_id_list
    # Cleanup
    impl_users.impl_delete_user_from_db(participant_user.id)
    impl_users.impl_delete_user_from_db(owner_user.id)
    impl.impl_delete_project(p.id)


def test_change_name_as_admin(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id)
    old_name = p.name
    new_name = tu.random_str(5, 50)
    # Act
    res = client.put(f'/api/core/projects/{p.id}/name?name={new_name}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    # Assert
    assert res.status_code == 200
    assert p_updated.name == new_name
    assert p_updated.name != old_name
    # Cleanup
    impl.impl_delete_project(p.id)


def test_change_name_as_non_admin(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    owner_user = tu_users.seed_random_user(admin=False, disabled=False)
    p = tu_projects.seed_random_project(owner_user.id, participants={
        current_user.id: models.AccessLevel.EDITOR
    })
    old_name = p.name
    new_name = tu.random_str(5, 50)
    # Act
    res = client.put(f'/api/core/projects/{p.id}/name?name={new_name}', headers=std_headers)
    p_updated = impl.impl_get_project(p.id)
    # Assert
    assert res.status_code == 403
    assert p_updated.name == old_name
    assert p_updated.name != new_name
    # Cleanup
    impl.impl_delete_project(p.id)
    impl_users.impl_delete_user_from_db(owner_user.id)


def test_add_participants_as_admin(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    participant_1 = tu_users.seed_random_user(admin=False, disabled=False)
    participant_2 = tu_users.seed_random_user(admin=False, disabled=False)
    participant_3 = tu_users.seed_random_user(admin=False, disabled=False)

    p = tu_projects.seed_random_project(current_user.id)

    participants_access_dict = {
        participant_1.id: models.AccessLevel.ADMIN,
        participant_2.id: models.AccessLevel.EDITOR,
        participant_3.id: models.AccessLevel.READONLY
    }

    # Act
    impl.impl_post_participants(p.id, participants_access_dict)
    p_updated = impl.impl_get_project(p.id)

    # Assert
    for participant in p_updated.participants:

        # Check owner
        if participant.id == current_user.id:
            assert p_updated.participants_access[participant.id] == models.AccessLevel.OWNER
            continue

        # Check other participants
        assert participant.id in participants_access_dict.keys()
        assert p_updated.participants_access[participant.id] == participants_access_dict[participant.id]

    # Cleanup
    impl.impl_delete_project(p.id)
    impl_users.impl_delete_user_from_db(participant_1.id)
    impl_users.impl_delete_user_from_db(participant_2.id)
    impl_users.impl_delete_user_from_db(participant_3.id)


def test_update_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    old_participant_1 = tu_users.seed_random_user(False, False)
    old_participant_2 = tu_users.seed_random_user(False, False)

    new_participant_1 = tu_users.seed_random_user(False, False)
    new_participant_2 = tu_users.seed_random_user(False, False)
    new_participant_3 = tu_users.seed_random_user(False, False)

    project = tu_projects.seed_random_project(current_user.id, participants={
        old_participant_1.id: models.AccessLevel.EDITOR,
        old_participant_2.id: models.AccessLevel.READONLY
    })

    # Add three subprojects to the project
    old_subproject_1 = tu_projects.seed_random_subproject(current_user.id, project.id)
    old_subproject_2 = tu_projects.seed_random_subproject(current_user.id, project.id)
    old_subproject_3 = tu_projects.seed_random_subproject(current_user.id, project.id)

    new_subproject_1 = tu_projects.seed_random_subproject(new_participant_3.id, None)
    new_subproject_2 = tu_projects.seed_random_subproject(current_user.id, None)

    new_name = tu.random_str(5, 50)

    # Act
    res_before = client.get(f'/api/core/projects/{project.id}', headers=std_headers)
    p_before_json = res_before.json()

    res_after = client.put(f'/api/core/projects/{project.id}', headers=std_headers, json={
        "id": project.id,
        "name": new_name,
        "participants_to_add": {
            new_participant_1.id: models.AccessLevel.ADMIN.value,
            new_participant_2.id: models.AccessLevel.EDITOR.value,
            new_participant_3.id: models.AccessLevel.READONLY.value
        },
        "participants_to_remove": [old_participant_1.id, old_participant_2.id],
        "subprojects_to_add": [new_subproject_1.id, new_subproject_2.id],
        "subprojects_to_remove": [old_subproject_1.id, old_subproject_2.id, old_subproject_3.id]
    })
    p_after_json = res_after.json()

    # Assert - before
    assert p_before_json["id"] == project.id
    assert len(p_before_json["participants"]) == 3
    assert len(p_before_json["subprojects"]) == 3
    assert p_before_json["name"] == project.name
    # Assert - after
    assert res_after.status_code == 200
    assert p_after_json["id"] == project.id
    assert p_after_json["name"] == new_name
    assert len(p_after_json["participants"]) == 4
    assert len(p_after_json["subprojects"]) == 2

    # Cleanup
    tu_users.delete_users([new_participant_1, new_participant_2, new_participant_3, old_participant_1, old_participant_2])

    old_subproject_1.project_id = None
    old_subproject_2.project_id = None
    old_subproject_3.project_id = None
    new_subproject_1.project_id = project.id
    new_subproject_2.project_id = project.id

    tu_projects.delete_subprojects([old_subproject_1, old_subproject_2, old_subproject_3, new_subproject_1, new_subproject_2])
    tu_projects.delete_projects([project])

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.vcs.implementation as impl_vcs


# ======================================================================================================================
# Get VCS
# ======================================================================================================================

def test_get_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_vcs_not_found(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs_id = 99999999
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs_id}', headers=std_headers)
    # Assert
    assert res.status_code == 404  # 404 Not Found
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_vcs_project_no_match(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    project2 = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project2.id}/vcs/{vcs.id}', headers=std_headers)
    # Assert
    assert res.status_code == 400  # 400 Bad Request
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# ======================================================================================================================
# Get all VCSs
# ======================================================================================================================

def test_get_vcss(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    tu.seed_random_vcs(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/all', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()["chunk"]) == 1
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# ======================================================================================================================
# Create VCS
# ======================================================================================================================

def test_create_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.random_VCS()
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/vcs', headers=std_headers, json=vcs.dict())
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(impl_vcs.get_all_vcs(project.id, current_user.id).chunk) == 1
    assert res.json()["name"] == vcs.name
    assert res.json()["description"] == vcs.description
    assert res.json()["year_from"] == vcs.year_from
    assert res.json()["year_to"] == vcs.year_to
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_vcs_year_from_greater_than_year_to(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.random_VCS()
    vcs.year_from = 2020
    vcs.year_to = 2019
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/vcs', headers=std_headers, json=vcs.dict())
    # Assert
    assert res.status_code == 400  # 400 Bad Request
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_vcs_missing_name(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.random_VCS()
    vcs.name = None
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/vcs', headers=std_headers, json=vcs.dict())
    # Assert
    assert res.status_code == 422  # 422 Unprocessable Entity
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# ======================================================================================================================
# Edit VCS
# ======================================================================================================================

def test_edit_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    vcs.name = "new name"
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}', headers=std_headers,
                     json={"name": vcs.name,
                           "description": vcs.description,
                           "year_from": vcs.year_from,
                           "year_to": vcs.year_to
                           })
    # Assert
    assert res.status_code == 200  # 200 OK
    assert impl_vcs.get_vcs(project.id, vcs.id, current_user.id).name == "new name"
    assert impl_vcs.get_vcs(project.id, vcs.id, current_user.id).description == vcs.description
    assert impl_vcs.get_vcs(project.id, vcs.id, current_user.id).year_from == vcs.year_from
    assert impl_vcs.get_vcs(project.id, vcs.id, current_user.id).year_to == vcs.year_to
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_vcs_year_from_greater_than_year_to(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    vcs.year_from = 2020
    vcs.year_to = 2019
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}', headers=std_headers,
                     json={"name": vcs.name,
                           "description": vcs.description,
                           "year_from": vcs.year_from,
                           "year_to": vcs.year_to
                           })
    # Assert
    assert res.status_code == 400  # 400 Bad Request
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# ======================================================================================================================
# Delete VCS
# ======================================================================================================================

def test_delete_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    # Act
    res = client.delete(f'/api/cvs/project/{project.id}/vcs/{vcs.id}', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(impl_vcs.get_all_vcs(project.id, current_user.id).chunk) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# ======================================================================================================================
# Duplicate VCS
# ======================================================================================================================

def test_duplicate_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/duplicate/{2}', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(impl_vcs.get_all_vcs(project.id, current_user.id).chunk) == 3
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

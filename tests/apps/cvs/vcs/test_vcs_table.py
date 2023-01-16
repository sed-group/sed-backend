import tests.apps.cvs.testutils as tu
import tests.testutils as core_tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.vcs.implementation as impl_vcs
import random


# ======================================================================================================================
# get VCS table
# ======================================================================================================================
def test_get_vcs_table(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 2)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/table', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 2
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_vcs_table_not_found(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs_id = 99999999
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs_id}/table', headers=std_headers)
    # Assert
    assert res.status_code == 404  # 404 Not Found
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_vcs_table(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    value_driver = tu.seed_random_value_driver(current_user.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/table', headers=std_headers,
                     json=[
                         {
                             "index": 0,
                             "iso_process": random.randint(1, 25),
                             "stakeholder": core_tu.random_str(5, 50),
                             "stakeholder_expectations": core_tu.random_str(5, 50),
                             "stakeholder_needs": [
                                 {
                                     "need": core_tu.random_str(5, 50),
                                     "rank_weight": random.random(),
                                     "value_dimension": core_tu.random_str(5, 50),
                                     "value_drivers": [
                                         value_driver.id
                                     ]
                                 }
                             ]
                         }
                     ]
                     )
    # Assert
    assert res.status_code == 200  # 200 OK
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_vcs_table(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    value_driver = tu.seed_random_value_driver(current_user.id)
    table = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)

    # Act
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/table', headers=std_headers,
                     json=[
                         {
                             "id": table[0].id,
                             "index": 0,
                             "iso_process": random.randint(1, 25),
                             "stakeholder": "new stakeholder",
                             "stakeholder_expectations": core_tu.random_str(5, 50),
                             "stakeholder_needs": [
                                 {
                                     "need": core_tu.random_str(5, 50),
                                     "rank_weight": random.random(),
                                     "value_dimension": core_tu.random_str(5, 50),
                                     "value_drivers": [
                                         value_driver.id
                                     ]
                                 }
                             ]
                         }
                     ]
                     )
    # Assert
    assert res.status_code == 200  # 200 OK
    assert impl_vcs.get_vcs_table(project.id, vcs.id)[0].stakeholder == 'new stakeholder'
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_delete_vcs_table(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    table = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 2)

    # Act
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/table', headers=std_headers,
                     json=[
                         {
                             "id": table[0].id,
                             "index": table[0].index,
                             "iso_process": 1,
                             "stakeholder": table[0].stakeholder,
                             "stakeholder_expectations": table[0].stakeholder_expectations
                         }
                     ]
                     )
    # Assert
    new_table = impl_vcs.get_vcs_table(project.id, vcs.id)
    assert res.status_code == 200  # 200 OK
    assert len(new_table) == 1
    assert any([row.id == table[0].id for row in new_table])
    assert any([row.id != table[1].id for row in new_table])
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


# TODO write more tests

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.vcs.implementation as impl_vcs
import sedbackend.apps.cvs.design.implementation as impl_design


def test_create_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/design-group', headers=std_headers, json={
        'name': "new design group",
    })
    # Assert
    design_groups = impl_design.get_all_design_groups(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(design_groups) == 1
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_create_design_group_no_name(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/design-group', headers=std_headers, json={
        'name': None,
    })
    # Assert
    design_groups = impl_design.get_all_design_groups(project.id)
    assert res.status_code == 422  # 422 unprocessable entity
    assert len(design_groups) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_create_design_group_from_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 10)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/design-group', headers=std_headers, json={
        'name': "new design group",
        'vcs_id': vcs.id,
    })
    # Assert
    design_groups = impl_design.get_all_design_groups(project.id)
    value_drivers = impl_vcs.get_all_value_driver_vcs(project.id, vcs.id)
    assert res.status_code == 200  # 200 OK
    assert len(design_groups) == 1
    assert len(value_drivers) == len(design_groups[0].vds)
    assert value_drivers[0].id == design_groups[0].vds[0].id
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_all_design_groups(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    tu.seed_random_design_group(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/design-group/all', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 1
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_all_design_groups_empty(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/design-group/all', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    dg = tu.seed_random_design_group(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/design-group/{dg.id}', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert res.json()['id'] == dg.id
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_design_group_not_found(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/design-group/999', headers=std_headers)
    # Assert
    assert res.status_code == 404  # 404 not found
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    dg = tu.seed_random_design_group(project.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{dg.id}', headers=std_headers, json={
        'name': "new name",
    })
    # Assert
    assert res.status_code == 200  # 200 OK
    assert res.json()['name'] == "new name"
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_add_value_driver_to_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    dg = tu.seed_random_design_group(project.id)
    vd = tu.seed_random_value_driver(current_user.id, project.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{dg.id}', headers=std_headers, json={
        'name': dg.name,
        'vd_ids': [vd.id],
    })
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()['vds']) == 1
    assert res.json()['vds'][0]['id'] == vd.id
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_remove_value_driver_from_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    dg = tu.seed_random_design_group(project.id)
    vd = tu.seed_random_value_driver(current_user.id, project.id)
    dg.vds.append(vd)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{dg.id}', headers=std_headers, json={
        'name': dg.name,
        'vd_ids': [],
    })
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()['vds']) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_delete_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    dg = tu.seed_random_design_group(project.id)
    # Act
    res = client.delete(f'/api/cvs/project/{project.id}/design-group/{dg.id}', headers=std_headers)
    # Assert
    design_groups = impl_design.get_all_design_groups(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(design_groups) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

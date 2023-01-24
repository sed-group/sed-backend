import random

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.design.implementation as impl_design


def test_create_design(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 10)  # To get value drivers to vcs
    design_group = tu.seed_random_design_group(project.id, None, vcs.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{design_group.id}/designs', headers=std_headers,
                     json=[{
                         'name': "new design",
                         'vd_design_values': [
                             {'vd_id': vd.id,
                              'value': round(random.random()*10, 4)} for vd in design_group.vds
                         ]
                     }
                     ])

    # Assert
    assert res.status_code == 200  # 200 OK
    designs = impl_design.get_all_designs(project.id, design_group.id)
    assert designs[0].name == "new design"
    assert len(designs) == 1
    assert len(designs[0].vd_design_values) == len(design_group.vds)

    # Cleanup
    tu.delete_vd_from_user(current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)
    


def test_create_design_no_values(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 10)  # To get value drivers to vcs
    design_group = tu.seed_random_design_group(project.id, None, vcs.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{design_group.id}/designs', headers=std_headers,
                     json=[{
                         'name': "new design",
                         'vd_design_values': []
                     }
                     ])

    # Assert
    assert res.status_code == 200  # 200 OK
    designs = impl_design.get_all_designs(project.id, design_group.id)
    assert len(designs) == 1

    # Cleanup
    tu.delete_vd_from_user(current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)
    


def test_edit_designs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 10)  # To get value drivers to vcs
    design_group = tu.seed_random_design_group(project.id, None, vcs.id)
    designs = tu.seed_random_designs(project.id, design_group.id, 1)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{design_group.id}/designs', headers=std_headers,
                     json=[{
                         'id': designs[0].id,
                         'name': "new design",
                         'vd_design_values': [
                             {'vd_id': vd.id,
                              'value': round(random.random()*10, 4)} for vd in design_group.vds
                         ]
                     }
                     ])

    # Assert
    assert res.status_code == 200  # 200 OK
    designs = impl_design.get_all_designs(project.id, design_group.id)
    assert designs[0].name == "new design"
    assert len(designs) == 1
    assert len(designs[0].vd_design_values) == len(design_group.vds)

    # Cleanup
    tu.delete_vd_from_user(current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)
    


def test_delete_designs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id, None, vcs.id)
    tu.seed_random_designs(project.id, design_group.id, 1)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/design-group/{design_group.id}/designs', headers=std_headers,
                     json=[])

    # Assert
    assert res.status_code == 200  # 200 OK
    designs = impl_design.get_all_designs(project.id, design_group.id)
    assert len(designs) == 0

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_all_designs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id, None, vcs.id)
    tu.seed_random_designs(project.id, design_group.id, 10)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/design-group/{design_group.id}/design/all', headers=std_headers)

    # Assert
    assert res.status_code == 200  # 200 OK
    designs = res.json()
    assert len(designs) == 10

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

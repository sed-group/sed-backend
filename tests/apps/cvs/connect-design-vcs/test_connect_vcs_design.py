import pytest

import tests.testutils as testutils
import tests.apps.cvs.testutils as tu

import sedbackend.apps.core.users.implementation as impl_users


def test_create_formulas(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    vcs_rows = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)
    if vcs_rows is None:
        raise Exception
    row_id = vcs_rows[0].id
    design_group = tu.seed_random_design_group(project.id)

    # Act
    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    # TODO when value drivers and market inputs are connected to the
    # formulas, add them here.
    value_driver_ids = []
    market_input_ids = []

    res = client.put(f'/api/cvs/project/{project.id}/vcs-row/{row_id}/design-group/{design_group.id}/formulas',
                     headers=std_headers,
                     json={
                         "time": time,
                         "time_unit": time_unit,
                         "cost": cost,
                         "revenue": revenue,
                         "rate": rate,
                         "value_driver_ids": value_driver_ids,
                         "market_input_ids": market_input_ids
                     })

    # Assert
    assert res.status_code == 200

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_create_formulas_no_optional(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    vcs_rows = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)
    if vcs_rows is None:
        raise Exception
    row_id = vcs_rows[0].id
    design_group = tu.seed_random_design_group(project.id)

    # Act
    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    res = client.put(f'/api/cvs/project/{project.id}/vcs-row/{row_id}/design-group/{design_group.id}/formulas',
                     headers=std_headers,
                     json={
                         "time": time,
                         "time_unit": time_unit,
                         "cost": cost,
                         "revenue": revenue,
                         "rate": rate
                     })

    # Assert
    assert res.status_code == 200
    assert res.json() == True

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_all_formulas(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id)

    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/design-group/{design_group.id}/formulas/all',
                     headers=std_headers)

    # Assert
    assert res.status_code == 200
    assert len(res.json()) == len(formulas)

    # Cleanup
    tu.delete_formulas(project.id, [(formula.vcs_row_id, formula.design_group_id) for formula in formulas])
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_all_formulas_invalid_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    invalid_proj_id = project.id + 1

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id)

    res = client.get(f'/api/cvs/project/{invalid_proj_id}/vcs/{vcs.id}/design-group/{design_group.id}/formulas/all',
                     headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_all_formulas_invalid_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    invalid_vcs_id = vcs.id + 1

    design_group = tu.seed_random_design_group(project.id)

    # Act
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id)

    res = client.get(f'/api/cvs/project/{project.id}/vcs/{invalid_vcs_id}/design-group/{design_group.id}/formulas/all',
                     headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)



def get_all_formulas_invalid_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)

    design_group = tu.seed_random_design_group(project.id)
    invalid_dg_id = design_group.id + 1

    # Act
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id)

    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/design-group/{invalid_dg_id}/formulas/all',
                     headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

def test_edit_formulas(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)

    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    # TODO when value drivers and market inputs are connected to the
    # formulas, add them here.
    value_driver_ids = []
    market_input_ids = []

    res = client.put(
        f'/api/cvs/project/{project.id}/vcs-row/{formulas[0].vcs_row_id}/design-group/{formulas[0].design_group_id}/formulas',
        headers=std_headers,
        json={
            "time": time,
            "time_unit": time_unit,
            "cost": cost,
            "revenue": revenue,
            "rate": rate,
            "value_driver_ids": value_driver_ids,
            "market_input_ids": market_input_ids
        })

    # Assert
    assert res.status_code == 200

    # Cleanup
    tu.delete_formulas(project.id, [(formula.vcs_row_id, formula.design_group_id) for formula in formulas])
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_formulas_no_optional(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)

    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    res = client.put(
        f'/api/cvs/project/{project.id}/vcs-row/{formulas[0].vcs_row_id}/design-group/{formulas[0].design_group_id}/formulas',
        headers=std_headers,
        json={
            "time": time,
            "time_unit": time_unit,
            "cost": cost,
            "revenue": revenue,
            "rate": rate
        })

    # Assert
    assert res.status_code == 200
    assert res.json() == True

    # Cleanup
    tu.delete_formulas(project.id, [(formula.vcs_row_id, formula.design_group_id) for formula in formulas])
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_formulas_invalid_dg(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    vcs_rows = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)
    if vcs_rows == None:
        raise Exception
    row_id = vcs_rows[0].id
    design_group = tu.seed_random_design_group(project.id)
    dg_invalid_id = design_group.id + 1

    # Act
    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    res = client.put(f'/api/cvs/project/{project.id}/vcs-row/{row_id}/design-group/{dg_invalid_id}/formulas',
                     headers=std_headers,
                     json={
                         "time": time,
                         "time_unit": time_unit,
                         "cost": cost,
                         "revenue": revenue,
                         "rate": rate
                     })

    # Assert
    assert res.status_code == 404

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_formulas_invalid_vcs_row(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    vcs_rows = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)
    if vcs_rows == None:
        raise Exception
    row_id = vcs_rows[0].id + 1
    design_group = tu.seed_random_design_group(project.id)

    # Act
    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    res = client.put(f'/api/cvs/project/{project.id}/vcs-row/{row_id}/design-group/{design_group.id}/formulas',
                     headers=std_headers,
                     json={
                         "time": time,
                         "time_unit": time_unit,
                         "cost": cost,
                         "revenue": revenue,
                         "rate": rate
                     })

    # Assert
    assert res.status_code == 404

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_formulas_invalid_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    invalid_proj_id = project.id + 1

    vcs = tu.seed_random_vcs(project.id)
    vcs_rows = tu.seed_vcs_table_rows(current_user.id, project.id, vcs.id, 1)
    if vcs_rows is None:
        raise Exception
    row_id = vcs_rows[0].id
    design_group = tu.seed_random_design_group(project.id)

    # Act
    time = testutils.random_str(10, 200)
    time_unit = tu.random_time_unit()
    cost = testutils.random_str(10, 200)
    revenue = testutils.random_str(10, 200)
    rate = tu.random_rate_choice()

    res = client.put(f'/api/cvs/project/{invalid_proj_id}/vcs-row/{row_id}/design-group/{design_group.id}/formulas',
                     headers=std_headers,
                     json={
                         "time": time,
                         "time_unit": time_unit,
                         "cost": cost,
                         "revenue": revenue,
                         "rate": rate
                     })

    # Assert
    assert res.status_code == 404

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_delete_formulas(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)

    res = client.delete(
        f'/api/cvs/project/{project.id}/vcs-row/{formulas[0].vcs_row_id}/design-group/{formulas[0].design_group_id}/formulas',
        headers=std_headers)

    # Assert
    assert res.status_code == 200

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)


def test_delete_formulas_invalid_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    invalid_proj_id = project.id + 1

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)

    res = client.delete(
        f'/api/cvs/project/{invalid_proj_id}/vcs-row/{formulas[0].vcs_row_id}/design-group/'
        f'{formulas[0].design_group_id}/formulas',
        headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

def test_delete_formulas_invalid_vcs_row(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)
    invalid_vcs_row_id = formulas[0].vcs_row_id + 1

    res = client.delete(
        f'/api/cvs/project/{project.id}/vcs-row/{invalid_vcs_row_id}/design-group/{formulas[0].design_group_id}/formulas',
        headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_delete_formulas_invalid_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)
    invalid_dg_id = design_group.id + 1

    # Act
    formulas = tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 1)

    res = client.delete(
        f'/api/cvs/project/{project.id}/vcs-row/{formulas[0].vcs_row_id}/design-group/{invalid_dg_id}/formulas',
        headers=std_headers)

    # Assert
    assert res.status_code == 400

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_vcs_dg_pairs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    vcss = [tu.seed_random_vcs(project.id) for _ in range(4)]
    dgs = [tu.seed_random_design_group(project.id) for _ in range(4)]

    formulas = []
    for i in range(4):
        formulas.append(tu.seed_random_formulas(project.id, vcss[i].id, dgs[i].id, current_user.id, 1))

    # Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/design/formula-pairs',
                     headers=std_headers)

    # Assert
    assert res.status_code == 200
    assert len(res.json()) == len(vcss) * len(dgs)

    # Cleanup
    tu.delete_formulas(project.id, [(formula[0].vcs_row_id, formula[0].design_group_id) for formula in formulas])
    [tu.delete_design_group(project.id, design_group.id) for design_group in dgs]
    tu.delete_VCS_with_ids(project.id, [vcs.id for vcs in vcss])
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_vcs_dg_pairs_invalid_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    invalid_proj_id = project.id + 1

    vcss = [tu.seed_random_vcs(project.id) for _ in range(4)]
    dgs = [tu.seed_random_design_group(project.id) for _ in range(4)]

    formulas = []
    for i in range(4):
        formulas.append(tu.seed_random_formulas(project.id, vcss[i].id, dgs[i].id, current_user.id, 1))

        # Act
    res = client.get(f'/api/cvs/project/{invalid_proj_id}/vcs/design/formula-pairs',
                     headers=std_headers)

    # Assert
    assert res.status_code == 404

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

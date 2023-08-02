import random

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.market_input.implementation as impl_market_input


def test_create_external_factor_value(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    external_factor = tu.seed_random_external_factor(project.id)
    value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[
        {
            'id': external_factor.id,
            'name': external_factor.name,
            'unit': external_factor.unit,
            'external_factor_values': [
                {'vcs_id': vcs.id, 'value': value}
            ]
        }
    ])
    # Assert
    efvs = impl_market_input.get_all_external_factor_values(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(efvs) == 1
    assert efvs[0].id == external_factor.id
    assert efvs[0].name == external_factor.name
    assert efvs[0].unit == external_factor.unit
    assert efvs[0].external_factor_values[0].vcs_id == vcs.id
    assert abs(efvs[0].external_factor_values[0].value - value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_external_factor_value_invalid_vcs_id(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_external_factor(project.id)
    value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-value', headers=std_headers, json=[
        {
            'id': market_input.id,
            'name': market_input.name,
            'unit': market_input.unit,
            'external_factor_values': {
                'vcs_id': vcs.id+1,
                'value': value
            }
        }
    ])
    # Assert
    assert res.status_code == 404  # 404 not found

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_external_factor_value(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    external_factor = tu.seed_random_external_factor(project.id)
    external_factor_value = tu.seed_random_external_factor_values(project.id, vcs.id, external_factor.id)[0]
    new_value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[
        {
            'id': external_factor_value.id,
            'name': external_factor_value.name,
            'unit': external_factor_value.unit,
            'external_factor_values': [
                {'vcs_id': vcs.id, 'value': new_value}
            ]
        }
    ])
    # Assert
    efvs = impl_market_input.get_all_external_factor_values(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(efvs) == 1
    assert efvs[0].id == external_factor_value.id
    assert efvs[0].name == external_factor_value.name
    assert efvs[0].unit == external_factor_value.unit
    assert efvs[0].external_factor_values[0].vcs_id == external_factor_value.external_factor_values[0].vcs_id
    assert abs(efvs[0].external_factor_values[0].value-new_value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_delete_market_input_value(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_external_factor(project.id)
    tu.seed_random_external_factor_values(project.id, vcs.id, market_input.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[])
    # Assert
    market_input_values = impl_market_input.get_all_external_factor_values(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(market_input_values) == 0

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_market_input_values(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    external_factor = tu.seed_random_external_factor(project.id)
    efv = tu.seed_random_external_factor_values(project.id, vcs.id, external_factor.id)[0]
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 1
    assert res.json()[0]['id'] == efv.id
    assert res.json()[0]['name'] == efv.name
    assert res.json()[0]['unit'] == efv.unit
    assert res.json()[0]['external_factor_values'][0]['vcs_id'] == efv.external_factor_values[0].vcs_id
    assert abs(res.json()[0]['external_factor_values'][0]['value'] - efv.external_factor_values[0].value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

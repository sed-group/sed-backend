import random

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.market_input.implementation as impl_market_input


def test_create_market_input(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[
        {
            'market_input_id': market_input.id,
            'vcs_id': vcs.id,
            'value': value
        }
    ])
    # Assert
    market_input_values = impl_market_input.get_all_market_values(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(market_input_values) == 1
    assert market_input_values[0].market_input_id == market_input.id
    assert market_input_values[0].vcs_id == vcs.id
    assert abs(market_input_values[0].value-value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_market_input_invalid_vcs_id(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[
        {
            'market_input_id': market_input.id,
            'vcs_id': vcs.id+1,
            'value': value
        }
    ])
    # Assert
    assert res.status_code == 404  # 404 not found

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_market_input_value(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    market_input_value = tu.seed_random_market_input_values(project.id, vcs.id, market_input.id)[0]
    new_value = random.random() * 100
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[
        {
            'market_input_id': market_input.id,
            'vcs_id': vcs.id,
            'value': new_value
        }
    ])
    # Assert
    market_input_values = impl_market_input.get_all_market_values(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(market_input_values) == 1
    assert market_input_values[0].market_input_id == market_input_value.market_input_id
    assert market_input_values[0].vcs_id == market_input_value.vcs_id
    assert abs(market_input_values[0].value-new_value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_delete_market_input_value(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(project.id, current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    tu.seed_random_market_input_values(project.id, vcs.id, market_input.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers, json=[])
    # Assert
    market_input_values = impl_market_input.get_all_market_values(project.id)
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
    market_input = tu.seed_random_market_input(project.id)
    market_input_value = tu.seed_random_market_input_values(project.id, vcs.id, market_input.id)[0]
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/market-input-values', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 1
    assert res.json()[0]['market_input_id'] == market_input_value.market_input_id
    assert res.json()[0]['vcs_id'] == market_input_value.vcs_id
    assert abs(res.json()[0]['value']-market_input_value.value) < 0.0001

    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.market_input.implementation as impl_market_input


def test_create_market_input(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/market-input', headers=std_headers, json={
        'name': "new market input",
        'unit': "new unit",
    })
    # Assert
    market_inputs = impl_market_input.get_all_market_inputs(project.id)
    assert res.status_code == 200  # 200 OK
    assert res.json()["name"] == "new market input"
    assert res.json()["unit"] == "new unit"
    assert len(market_inputs) == 1
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_create_market_input_no_name(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.post(f'/api/cvs/project/{project.id}/market-input', headers=std_headers, json={
        'name': None,
        'unit': "new unit",
    })
    # Assert
    assert res.status_code == 422  # 422 unprocessable entity
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_all_market_inputs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/market-input/all', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert res.json()[0]["id"] == market_input.id
    assert len(res.json()) == 1
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_get_all_market_inputs_no_market_inputs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    # Act
    res = client.get(f'/api/cvs/project/{project.id}/market-input/all', headers=std_headers)
    # Assert
    assert res.status_code == 200  # 200 OK
    assert len(res.json()) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_market_input(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input/{market_input.id}', headers=std_headers, json={
        'name': "new market input",
        'unit': "new unit",
    })
    # Assert
    market_input_updated = impl_market_input.get_market_input(project.id, market_input.id)
    assert res.status_code == 200  # 200 OK
    assert market_input_updated.name == "new market input"
    assert market_input_updated.unit == "new unit"
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_market_input_no_changes(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input/{market_input.id}', headers=std_headers, json={
        'name': market_input.name,
        'unit': market_input.unit,
    })
    # Assert
    market_input_updated = impl_market_input.get_market_input(project.id, market_input.id)
    assert res.status_code == 200  # 200 OK
    assert market_input_updated.name == market_input.name
    assert market_input_updated.unit == market_input.unit
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_edit_market_input_no_name(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    # Act
    res = client.put(f'/api/cvs/project/{project.id}/market-input/{market_input.id}', headers=std_headers, json={
        'name': None,
        'unit': market_input.unit,
    })
    # Assert
    assert res.status_code == 422  # 422 unprocessable entity
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_delete_market_input(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    market_input = tu.seed_random_market_input(project.id)
    # Act
    res = client.delete(f'/api/cvs/project/{project.id}/market-input/{market_input.id}', headers=std_headers)
    # Assert
    market_inputs = impl_market_input.get_all_market_inputs(project.id)
    assert res.status_code == 200  # 200 OK
    assert len(market_inputs) == 0
    # Cleanup
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

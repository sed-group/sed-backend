import tests.apps.cvs.testutils as tu
import testutils as sim_tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.simulation.exceptions as sim_exceptions


def test_run_single_monte_carlo_sim(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = True
    settings.runs = 5

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 200

    # Should probably assert some other stuff about the output to ensure that it is correct.

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_invalid_design_group(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = True
    settings.runs = 5

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id + 9999]
                      })

    # Assert
    assert res.status_code == 400

    # Should probably assert some other stuff about the output to ensure that it is correct.

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_invalid_vcss(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = True
    settings.runs = 5

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id + 9999],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 400

    # Should probably assert some other stuff about the output to ensure that it is correct.

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_end_time_before_start_time(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = False
    settings.end_time = settings.start_time - 1

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 400
    assert res.json() == {'detail': 'Settings are not correct'}  # Should raise BadlyFormattedSettingsException

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_no_flows(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = False
    settings.flow_start_time = None
    settings.flow_process = None

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 400
    assert res.json() == {'detail': 'Settings are not correct'}  # Should raise BadlyFormattedSettingsException

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_both_flows(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    settings.monte_carlo = False
    settings.flow_start_time = 5
    settings.flow_process = 10

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 400
    assert res.json() == {'detail': 'Settings are not correct'}  # Should raise BadlyFormattedSettingsException

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_rate_invalid_order(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)

    project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
    first_tech_process = tu.edit_rate_order_formulas(project.id, vcs.id, design_group.id, current_user.id)
    if first_tech_process is None:
        raise sim_exceptions.NoTechnicalProcessException
    settings.monte_carlo = False

    # Act
    res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing',
                      headers=std_headers,
                      json={
                          "sim_settings": settings.dict(),
                          "vcs_ids": [vcs.id],
                          "design_group_ids": [design_group.id]
                      })

    # Assert
    assert res.status_code == 400

    # Cleanup
    tu.delete_design_group(project.id, design_group.id)
    tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
    tu.delete_project_by_id(project.id, current_user.id)
    tu.delete_vd_from_user(current_user.id)

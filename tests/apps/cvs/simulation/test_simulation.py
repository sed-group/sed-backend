import pytest
import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users

def test_get_sim_settings(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)

  #Act
  res = client.get(f'/api/cvs/project/{project.id}/simulation/settings', headers=std_headers)

  #Assert 
  assert res.status_code == 200
  assert res.json()["time_unit"] == sim_settings.time_unit
  assert res.json()["end_time"] == sim_settings.end_time

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


def test_get_sim_settings_invalid_proj(client, std_headers):
  pass


def test_edit_sim_settings(client, std_headers, std_user):
  pass


def test_edit_sim_settings_both_flows(client, std_headers, std_user):
  pass


def test_edit_sim_settings_no_flows(client, std_headers, std_user):
  pass


def test_edit_sim_settings_invalid_proj(client, std_headers, std_user):
  pass


def test_run_simulation(client, std_headers, std_user):
  pass


def test_run_sim_invalid_designs(client, std_headers, std_user):
  pass


def test_run_sim_invalid_vcss(client, std_headers, std_user):
  pass


def test_run_sim_end_time_before_start_time(client, std_headers, std_user):
  pass


def test_run_sim_flow_time_above_total_time(client, std_headers, std_user):
  pass


def test_run_sim_no_flows(client, std_headers, std_user):
  pass


def test_run_sim_both_flows(client, std_headers, std_user):
  pass


def test_run_sim_rate_invalid_order(client, std_headers, std_user):
  pass


def test_run_sim_invalid_proj(client, std_headers, std_user):
  pass



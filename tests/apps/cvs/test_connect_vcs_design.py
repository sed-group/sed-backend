import pytest

import tests.testutils as testutils
import tests.apps.cvs.testutils as tu

import sedbackend.apps.core.users.implementation as impl_users

def test_create_formulas(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)

  vcs = tu.seed_random_vcs(current_user.id, project.id)
  vcs_rows = tu.seed_vcs_table_rows(vcs.id, project.id, current_user.id, 1)
  if vcs_rows == None:
    raise Exception
  row_id = vcs_rows[0].id
  design_group = tu.seed_random_design_group(project.id)

  #Act
  time = testutils.random_str(10,200)
  time_unit = tu.random_time_unit()
  cost = testutils.random_str(10, 200)
  revenue = testutils.random_str(10, 200)
  rate = tu.random_rate_choice()

  #TODO when value drivers and market inputs are connected to the 
  #formulas, add them here. 
  value_driver_ids = []
  market_input_ids = []

  res = client.put(f'/api/cvs/project/{project.id}/vcs-row/{row_id}/design-group/{design_group.id}/formulas',
                  headers=std_headers,
                  json = {
                    "time": time,
                    "time_unit": time_unit,
                    "cost": cost,
                    "revenue": revenue,
                    "rate": rate,
                    "value_driver_ids": value_driver_ids,
                    "market_input_ids": market_input_ids
                  })

  #Assert
  assert res.status_code == 200
  

  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids([vcs.id], project.id)
  tu.delete_project_by_id(project.id, current_user.id)


def test_get_all_formulas(client, std_headers, std_user):
  pass


def test_edit_formulas(client, std_headers, std_user):
  pass


def test_delete_formulas(client, std_headers, std_user):
  pass


def test_get_vcs_dg_pairs(client, std_headers, std_user):
  pass

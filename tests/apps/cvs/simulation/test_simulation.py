import pytest
import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users

def test_run_single_simulation(client, std_headers, std_user):
  #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcs = tu.seed_random_vcs(current_user.id, project.id)
  design_group = tu.seed_random_design_group(project.id)
  tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 10) #Also creates the vcs rows
  design = tu.seed_random_designs(project.id, design_group.id, 1)

  settings = tu.seed_simulation_settings(project.id, [vcs.id], [design[0].id])
  settings.monte_carlo = False

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  print(res)
  assert res.status_code == 200
  #Should probably assert some other stuff about the output to ensure that it is correct. 
  

  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids([vcs.id], project.id)
  tu.delete_project_by_id(project.id, current_user.id)


def test_run_simulation(client, std_headers, std_user):
  #Setup
  amount = 3

  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcss = []
  dgs = []

  design_ids = []

  #TODO Find a way to get a row that is the same across all vcs's - so that there is an interarrival process
  for _ in range(amount):
    vcs = tu.seed_random_vcs(current_user.id, project.id)
    design_group = tu.seed_random_design_group(project.id)
    vcss.append(vcs)
    dgs.append(design_group)
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 10) #Also creates the vcs rows
    design = tu.seed_random_designs(project.id, design_group.id, 1)
    design_ids.append(design[0].id)
  
  tu.seed_formulas_for_multiple_vcs(project.id, [vcs.id for vcs in vcss], [dg.id for dg in dgs], current_user.id)

  settings = tu.seed_simulation_settings(project.id, [vcs.id for vcs in vcss], design_ids)
  settings.monte_carlo = False

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  assert res.status_code == 200
  #Should probably assert some other stuff about the output to ensure that it is correct. 
  

  #Cleanup
  for dg in dgs:
    tu.delete_design_group(project.id, dg.id)

  tu.delete_VCS_with_ids([vcs.id for vcs in vcss], project.id)
  tu.delete_project_by_id(project.id, current_user.id)


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


def test_run_sim_monte_carlo(client, std_headers, std_user):
  pass


def test_run_xlsx_sim(client, std_headers, std_user):
  pass


def test_run_csv_sim(client, std_headers, std_user):
  pass
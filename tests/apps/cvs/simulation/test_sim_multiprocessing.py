import pytest
import tests.apps.cvs.testutils as tu
import testutils as sim_tu
import sedbackend.apps.core.users.implementation as impl_users

def test_run_single_monte_carlo_sim(client, std_headers, std_user):
  #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)

  project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
  settings.monte_carlo = True
  settings.runs = 5

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
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
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids(project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_invalid_designs(client, std_headers, std_user):
      #Setup
  amount = 2

  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcss = []
  dgs = []

  design_ids = []

  #TODO Find a way to get a row that is the same across all vcs's - so that there is an interarrival process
  for _ in range(amount):
    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)
    vcss.append(vcs)
    dgs.append(design_group)
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 10) #Also creates the vcs rows
    design = tu.seed_random_designs(project.id, design_group.id, 1)
    design_ids.append(design[0].id + 7000)
  
  tu.seed_formulas_for_multiple_vcs(project.id, [vcs.id for vcs in vcss], [dg.id for dg in dgs], current_user.id)

  settings = tu.seed_simulation_settings(project.id, [vcs.id for vcs in vcss], design_ids)
  settings.monte_carlo = False

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id for vcs in vcss],
                      "design_ids": design_ids
                    })
  
  #Assert
  assert res.status_code == 400
  assert res.json() == {'detail': 'Could not find design'} #The error from get_design() in design.implementation

  #Cleanup
  tu.delete_VCS_with_ids(project.id, [vcs.id for vcs in vcss])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_invalid_vcss(client, std_headers, std_user):
  #Setup
  amount = 2

  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcss = []
  dgs = []

  design_ids = []

  #TODO Find a way to get a row that is the same across all vcs's - so that there is an interarrival process
  for _ in range(amount):
    vcs = tu.seed_random_vcs(project.id)
    design_group = tu.seed_random_design_group(project.id)
    vcss.append(vcs)
    dgs.append(design_group)
    tu.seed_random_formulas(project.id, vcs.id, design_group.id, current_user.id, 15) #Also creates the vcs rows
    design = tu.seed_random_designs(project.id, design_group.id, 1)
    design_ids.append(design[0].id)
  
  tu.seed_formulas_for_multiple_vcs(project.id, [vcs.id for vcs in vcss], [dg.id for dg in dgs], current_user.id)

  settings = tu.seed_simulation_settings(project.id, [vcs.id for vcs in vcss], design_ids)
  settings.monte_carlo = False

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [(vcs.id + 4000) for vcs in vcss],
                      "design_ids": design_ids
                    })
  
  #Assert
  #print(res.json())
  assert res.status_code == 400
  #Should probably assert some other stuff about the output to ensure that it is correct. 
  

  #Cleanup
  for dg in dgs:
    tu.delete_design_group(project.id, dg.id)

  tu.delete_VCS_with_ids(project.id, [vcs.id for vcs in vcss])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_end_time_before_start_time(client, std_headers, std_user):
  #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)

  project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
  settings.monte_carlo = False
  settings.end_time = settings.start_time - 1

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  assert res.status_code == 400
  assert res.json() == {'detail': 'Settings are not correct'} #Should raise BadlyFormattedSettingsException
  
  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids(project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_no_flows(client, std_headers, std_user):
   #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)

  project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
  settings.monte_carlo = False
  settings.flow_start_time = None
  settings.flow_process = None

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  assert res.status_code == 400
  assert res.json() == {'detail': 'Settings are not correct'} #Should raise BadlyFormattedSettingsException
  
  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids(project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_both_flows(client, std_headers, std_user):
      #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)

  project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
  settings.monte_carlo = False
  settings.flow_start_time = 5
  settings.flow_process = 10

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  assert res.status_code == 400
  assert res.json() == {'detail': 'Settings are not correct'} #Should raise BadlyFormattedSettingsException
  
  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids(project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_run_mc_sim_rate_invalid_order(client, std_headers, std_user):
    #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)

  project, vcs, design_group, design, settings = sim_tu.setup_single_simulation(current_user.id)
  tu.edit_rate_order_formulas(project.id, vcs.id, design_group.id)
  settings.monte_carlo = False

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/simulation/run-multiprocessing', 
                    headers=std_headers,
                    json = {
                      "sim_settings": settings.dict(),
                      "vcs_ids": [vcs.id],
                      "design_ids": [design[0].id]
                    })
  
  #Assert
  assert res.status_code == 400
  assert res.json() == {'detail': 'Wrong order of rate of entities. Per project assigned after per product'} #RateWrongOrderException
  

  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids(project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)

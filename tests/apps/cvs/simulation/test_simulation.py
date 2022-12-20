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


def test_get_sim_settings_invalid_proj(client, std_user, std_headers):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)

  invalid_proj = project.id + 1

  #Act
  res = client.get(f'/api/cvs/project/{invalid_proj}/simulation/settings', headers=std_headers)

  #Assert
  assert res.status_code == 404

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


def test_edit_sim_settings(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)

  #Act
  flow_time = round(tu.random.uniform(1, 300), ndigits=5) #Should probs check that this is correct with the other settings
  interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
  discount_rate = round(tu.random.random(), ndigits=5)

  res = client.put(f'/api/cvs/project/{project.id}/simulation/settings', 
                    headers=std_headers, 
                    json = {
                      "project": project.id,
                      "time_unit": sim_settings.time_unit,
                      "flow_process": sim_settings.flow_process,
                      "flow_start_time": sim_settings.flow_start_time,
                      "flow_time": flow_time,
                      "interarrival_time": interarrival_time,
                      "start_time": sim_settings.start_time,
                      "end_time": sim_settings.end_time,
                      "discount_rate": discount_rate,
                      "non_tech_add": sim_settings.non_tech_add.value,
                      "monte_carlo": sim_settings.monte_carlo,
                      "runs": sim_settings.runs
                    })

  #Assert
  assert res.status_code == 200
  assert res.json() == True

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


def test_edit_sim_settings_both_flows(client, std_headers, std_user):
    #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)

  #Act
  flow_start_time = round(tu.random.uniform(1, 50), ndigits=5)
  flow_process = 10
  flow_time = round(tu.random.uniform(1, 300), ndigits=5) #Should probs check that this is correct with the other settings
  interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
  discount_rate = round(tu.random.random(), ndigits=5)

  res = client.put(f'/api/cvs/project/{project.id}/simulation/settings', 
                    headers=std_headers, 
                    json = {
                      "project": project.id,
                      "time_unit": sim_settings.time_unit,
                      "flow_process": flow_process,
                      "flow_start_time": flow_start_time,
                      "flow_time": flow_time,
                      "interarrival_time": interarrival_time,
                      "start_time": sim_settings.start_time,
                      "end_time": sim_settings.end_time,
                      "discount_rate": discount_rate,
                      "non_tech_add": sim_settings.non_tech_add.value,
                      "monte_carlo": sim_settings.monte_carlo,
                      "runs": sim_settings.runs
                    })

  #Assert
  assert res.status_code == 400

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


def test_edit_sim_settings_no_flows(client, std_headers, std_user):
      #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)

  #Act
  flow_start_time = None
  flow_process = None
  flow_time = round(tu.random.uniform(1, 300), ndigits=5) #Should probs check that this is correct with the other settings
  interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
  discount_rate = round(tu.random.random(), ndigits=5)

  res = client.put(f'/api/cvs/project/{project.id}/simulation/settings', 
                    headers=std_headers, 
                    json = {
                      "project": project.id,
                      "time_unit": sim_settings.time_unit,
                      "flow_process": flow_process,
                      "flow_start_time": flow_start_time,
                      "flow_time": flow_time,
                      "interarrival_time": interarrival_time,
                      "start_time": sim_settings.start_time,
                      "end_time": sim_settings.end_time,
                      "discount_rate": discount_rate,
                      "non_tech_add": sim_settings.non_tech_add.value,
                      "monte_carlo": sim_settings.monte_carlo,
                      "runs": sim_settings.runs
                    })

  #Assert
  assert res.status_code == 400

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


def test_edit_sim_settings_invalid_proj(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  sim_settings = tu.seed_random_sim_settings(project.id)
  invalid_proj = project.id + 1


  #Act
  flow_start_time = round(tu.random.uniform(1, 50), ndigits=5)
  flow_process = 10
  flow_time = round(tu.random.uniform(1, 300), ndigits=5) #Should probs check that this is correct with the other settings
  interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
  discount_rate = round(tu.random.random(), ndigits=5)

  res = client.put(f'/api/cvs/project/{invalid_proj}/simulation/settings', 
                    headers=std_headers, 
                    json = {
                      "project": invalid_proj,
                      "time_unit": sim_settings.time_unit,
                      "flow_process": flow_process,
                      "flow_start_time": flow_start_time,
                      "flow_time": flow_time,
                      "interarrival_time": interarrival_time,
                      "start_time": sim_settings.start_time,
                      "end_time": sim_settings.end_time,
                      "discount_rate": discount_rate,
                      "non_tech_add": sim_settings.non_tech_add.value,
                      "monte_carlo": sim_settings.monte_carlo,
                      "runs": sim_settings.runs
                    })

  #Assert
  assert res.status_code == 404

  #Cleanup
  tu.delete_project_by_id(project.id, current_user.id)


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
  assert res.status_code == 200
  #Should probably assert some other stuff about the output to ensure that it is correct. 
  

  #Cleanup
  tu.delete_design_group(project.id, design_group.id)
  tu.delete_VCS_with_ids([vcs.id], project.id)
  tu.delete_project_by_id(project.id, current_user.id)




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



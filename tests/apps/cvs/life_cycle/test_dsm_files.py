import pytest
import os
from pathlib import Path
import tests.apps.cvs.testutils as tu
import sedbackend.apps.core.users.implementation as impl_users
import sedbackend.apps.cvs.life_cycle.implementation as impl_life_cycle
import sedbackend.apps.core.files.implementation as impl_files


def test_upload_dsm_file(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcs = tu.seed_random_vcs(project.id)
  
  row1 = tu.vcs_model.VcsRowPost(
    index=0,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=17,
    subprocess=None
  )
  row2 = tu.vcs_model.VcsRowPost(
    index=1,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=20,
    subprocess=None
  )
  
  rows = [row1, row2]
  table = tu.create_vcs_table(project.id, vcs.id, rows)
  
  cwd = os.getcwd()
  _test_upload_file = Path(cwd + '/tests/apps/cvs/life_cycle/files/input.csv')
  _file = {'file': ('input.csv', _test_upload_file.open('rb'), 'text/csv')}
  

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/upload-dsm',
                    headers=std_headers,
                    files=_file)

  #Assert
  assert res.status_code == 200
  
  #Cleanup
  tu.delete_dsm_file_from_vcs_id(project.id, vcs.id, current_user.id)
  tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  
  
def test_upload_invalid_file_extension(client, std_headers, std_user):
  #Setup 
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcs = tu.seed_random_vcs(project.id)

  row1 = tu.vcs_model.VcsRowPost(
    index=0,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=17,
    subprocess=None
  )
  row2 = tu.vcs_model.VcsRowPost(
    index=1,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=20,
    subprocess=None
  )
  row3 = tu.vcs_model.VcsRowPost(
    index=2,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=22,
    subprocess=None
  )
  row4 = tu.vcs_model.VcsRowPost(
    index=3,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=24,
    subprocess=None
  )
  
  rows = [row1, row2, row3, row4]

  table = tu.create_vcs_table(project.id, vcs.id, rows)

  cwd = os.getcwd()
  _test_upload_file = Path(cwd + '/tests/apps/cvs/life_cycle/files/input-example.xlsx')
  _file = {'file': ('input-example.xlsx', _test_upload_file.open('rb'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}

  #Act 
  res = client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/upload-dsm',
                    headers=std_headers,
                    files=_file)
  
  #Assert
  assert res.status_code == 415 #InvalidFileTypeException
  

  #Cleanup
  tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
  tu.delete_vd_from_user(current_user.id)


def test_upload_invalid_dsm_file(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcs = tu.seed_random_vcs(project.id)
  
  row1 = tu.vcs_model.VcsRowPost(
    index=0,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=17,
    subprocess=None
  )
  row2 = tu.vcs_model.VcsRowPost(
    index=1,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=15,
    subprocess=None
  )
  
  rows = [row1, row2]
  table = tu.create_vcs_table(project.id, vcs.id, rows)
  
  cwd = os.getcwd()
  _test_upload_file = Path(cwd + '/tests/apps/cvs/life_cycle/files/input.csv')
  _file = {'file': ('input.csv', _test_upload_file.open('rb'), 'text/csv')}
  

  #Act
  res = client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/upload-dsm',
                    headers=std_headers,
                    files=_file)

  #Assert
  assert res.status_code == 400 #Bad request, should throw ProcessesVcsMatchException
  
  #Cleanup
  tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)


def test_get_dsm_file_id(client, std_headers, std_user):
  #Setup
  current_user = impl_users.impl_get_user_with_username(std_user.username)
  project = tu.seed_random_project(current_user.id)
  vcs = tu.seed_random_vcs(project.id)
  
  row1 = tu.vcs_model.VcsRowPost(
    index=0,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=17,
    subprocess=None
  )
  row2 = tu.vcs_model.VcsRowPost(
    index=1,
    stakeholder=tu.tu.random_str(5,50),
    stakeholder_needs=None,
    stakeholder_expectations=tu.tu.random_str(5,50),
    iso_process=20,
    subprocess=None
  )
  
  rows = [row1, row2]
  table = tu.create_vcs_table(project.id, vcs.id, rows)
  
  cwd = os.getcwd()
  _test_upload_file = Path(cwd + '/tests/apps/cvs/life_cycle/files/input.csv')
  _file = {'file': ('input.csv', _test_upload_file.open('rb'), 'text/csv')}
  

  #Act
  client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/upload-dsm',
                    headers=std_headers,
                    files=_file)

  res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/get-dsm-id',
                    headers=std_headers)

  #Assert
  assert res.status_code == 200
  
  #Cleanup
  tu.delete_dsm_file_from_vcs_id(project.id, vcs.id, current_user.id)
  tu.delete_VCS_with_ids(current_user.id, project.id, [vcs.id])
  tu.delete_project_by_id(project.id, current_user.id)
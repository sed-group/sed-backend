import json
from pydoc import cli
import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import tests.apps.cvs.testutils as tu
import tests.testutils as testutils
import sedbackend.apps.core.users.implementation as impl_users


def test_get_VCS(client, std_headers, std_user):
    # Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    current_project = tu.seed_random_project(current_user.id)
    seeded_VCS = tu.seed_random_vcs(current_user.id, current_project.id)

    #Act
    res = client.get(f'/api/cvs/project/{current_project.id}/vcs/get/{seeded_VCS.id}', headers=std_headers)

    # Assert
    assert res.status_code == 200
    
    # Cleanup
    tu.delete_VCSs([seeded_VCS], current_project.id, current_user.id)

def test_create_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    # Act 
    res = client.post(f"/api/cvs/project/{project.id}/vcs/create",
                    headers=std_headers,
                    json={
                        "name":  testutils.random_str(3, 30),
                        "description": testutils.random_str(20, 200),
                        "year_from": r.randint(2019, 2060),
                        "year_to": r.randint(2020, 2100)
                    })
    # Assert
    assert res.status_code == 200
#    assert impl.get_vcs(res.json["id"], project.id, current_user.id) is not None

    # Cleanup
    tu.delete_VCS_with_ids([res.json()["id"]],project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_edit_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, project.id)

    #Act
    new_name = testutils.random_str(5,50)
    new_desc = testutils.random_str(20,200)
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/edit',
                    headers=std_headers,
                    json= {
                        "name": new_name,
                        "description": new_desc,
                        "year_from": r.randint(0, 4000),
                        "year_to": r.randint(0, 5000)
                    })
    
    # assert
    assert res.status_code == 200
    assert res.json()["name"] == new_name
    assert res.json()["description"] == new_desc

    #Cleanup 
    tu.delete_VCS_with_ids([res.json()["id"]],project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_edit_vcs_same_years(client, std_headers, std_user):
     # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, project.id)

    #Act
    new_name = testutils.random_str(5,50)
    new_desc = testutils.random_str(20,200)
    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/edit',
                    headers=std_headers,
                    json= {
                        "name": new_name,
                        "description": new_desc
                    })
    
    # assert
    assert res.status_code == 200
    assert res.json()["name"] == new_name
    assert res.json()["description"] == new_desc
    assert vcs.year_from == res.json()["year_from"]

    #Cleanup 
    tu.delete_VCS_with_ids([res.json()["id"]],project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_delete_vcs(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, project.id)

    #Act
    res = client.delete(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/delete')

    #Assert
    res.status_code = 200

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

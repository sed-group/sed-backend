import json
from pydoc import cli
import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.project.models as models
import sedbackend.apps.cvs.project.implementation
import tests.apps.cvs.testutils as tu
import tests.testutils as testutils
import sedbackend.apps.core.users.implementation as impl_users


def test_create_cvs_project(client, admin_headers):
    # Act 
    res = client.post("/api/cvs/project",
                    headers=admin_headers,
                    json={
                        "name":  testutils.random_str(3, 30),
                        "description": testutils.random_str(20, 200)
                    })

    # Assert
    assert res.status_code == 200

    # cleanup
    sedbackend.apps.cvs.project.implementation.delete_cvs_project(res.json()["id"], res.json()["owner"]["id"])

def test_delete_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    # Act

    res = client.delete(f'/api/cvs/project/{project.id}', headers=std_headers)

    # Assert
    assert res.status_code == 200



def test_edit_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    #Act
    name = testutils.random_str(5,50)
    res = client.put(f'/api/cvs/project/{project.id}', 
                        headers=std_headers,
                        json = {
                            "name": name,
                            "description": testutils.random_str(20, 200)
                        })
    
    # Assert
    assert res.status_code == 200
    assert res.json()["name"] == name

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

def test_get_cvs_project(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    #Act
    res = client.get(f'/api/cvs/project/{project.id}',
                        headers=std_headers)
    
    # Assert
    assert res.status_code == 200
    assert res.json()["id"] == project.id
    assert res.json()["name"] == project.name

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

def test_get_all_cvs_projects(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    proj1 = tu.seed_random_project(current_user.id)
    proj2 = tu.seed_random_project(current_user.id)
    proj3 = tu.seed_random_project(current_user.id)

    #Act
    res = client.get(f'/api/cvs/project/all', headers=std_headers)

    #Assert
    assert res.status_code == 200
    assert res.json()["chunk"][0]["id"] == proj1.id
    assert res.json()["chunk"][1]["id"] == proj2.id
    assert res.json()["chunk"][2]["id"] == proj3.id

    #Cleanup
    tu.delete_project_by_id(proj1.id, current_user.id)
    tu.delete_project_by_id(proj2.id, current_user.id)
    tu.delete_project_by_id(proj3.id, current_user.id)
    
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
    #Setup
    name = testutils.random_str(3, 30)
    description = testutils.random_str(20, 200)
    currency = testutils.random_str(0, 10)
    
    # Act 
    res = client.post("/api/cvs/project",
                    headers=admin_headers,
                    json={
                        "name":  name,
                        "description": description,
                        "currency": currency
                    })

    # Assert
    assert res.status_code == 200
    assert res.json()["name"] == name
    assert res.json()["description"] == description
    assert res.json()["currency"] == currency

    # cleanup
    sedbackend.apps.cvs.project.implementation.delete_cvs_project(res.json()["id"], res.json()["owner"]["id"])


def test_create_only_name_project(client, std_headers):
    #Setup
    name = testutils.random_str(3, 255)

    #Act
    res = client.post("/api/cvs/project",
                    headers=std_headers,
                    json={
                        "name": name
                    })
    
    #Assert
    assert res.status_code == 200
    assert res.json()["name"] == name
    assert res.json()["currency"] == None
    assert res.json()["description"] == None

    #cleanup
    tu.delete_project_by_id(res.json()["id"], res.json()["owner"]["id"])


def test_create_no_name_project(client, std_headers):
    #Act
    res1 = client.post("/api/cvs/project",
                    headers=std_headers,
                    json={
                        "description": testutils.random_str(20,200),
                        "currency": testutils.random_str(0,10)
                    })

    #Assert
    assert res1.status_code == 422
    

def test_create_too_long_currency_project(client, std_headers):
    #Act
    res2 = client.post("/api/cvs/project",
                headers=std_headers,
                json={
                    "name": testutils.random_str(3, 30),
                    "description": testutils.random_str(20, 200),
                    "currency": testutils.random_str(11, 50)
                })

    #Assert
    assert res2.status_code == 422


def test_create_too_long_name_project(client, std_headers):
        #Act
    res2 = client.post("/api/cvs/project",
                headers=std_headers,
                json={
                    "name": testutils.random_str(255, 300),
                    "description": testutils.random_str(20, 200),
                    "currency": testutils.random_str(0, 10)
                })

    #Assert
    assert res2.status_code == 422


def test_delete_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    # Act
    res = client.delete(f'/api/cvs/project/{project.id}', headers=std_headers)

    # Assert
    assert res.status_code == 200
    assert res.json() == True


def test_delete_wrong_cvs_project(client, std_headers, std_user):
    #setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    wrong_id = project.id + 1

    #Act
    res = client.delete(f'/api/cvs/project/{wrong_id}', headers=std_headers)

    #Assert
    assert res.status_code == 404 #Should fail on accesslevelchecker

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)



def test_edit_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)


    name = testutils.random_str(5,50)
    description = testutils.random_str(20, 200)
    currency = testutils.random_str(0, 10)
    #Act

    res = client.put(f'/api/cvs/project/{project.id}', 
                        headers=std_headers,
                        json = {
                            "name": name,
                            "description": description,
                            "currency": currency
                        })
    
    # Assert
    assert res.status_code == 200
    assert res.json()["name"] == name
    assert res.json()["currency"] == currency and res.json()["currency"] != project.currency
    assert res.json()["description"] == description


    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_cvs_project_only_name(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)


    name = testutils.random_str(5,50)
    
    #Act
    res = client.put(f'/api/cvs/project/{project.id}', 
                        headers=std_headers,
                        json = {
                            "name": name
                        })
    
    #Assert
    assert res.status_code == 200
    assert res.json()["name"] == name
    assert res.json()["description"] == None

    #cleanup
    tu.delete_project_by_id(project.id, current_user.id)


def test_edit_cvs_project_same(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    
    #Act
    res = client.put(f'/api/cvs/project/{project.id}', 
                        headers=std_headers,
                        json = {
                            "name": project.name,
                            "description": project.description,
                            "currency": project.currency
                        })
    
    #Assert
    assert res.status_code == 200
    assert res.json()["name"] == project.name
    assert res.json()["description"] == project.description
    assert res.json()["currency"] == project.currency

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


def test_get_wrong_cvs_project(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    wrong_proj_id = project.id + 1
    
    #Act
    res = client.get(f'/api/cvs/project/{wrong_proj_id}',
                    headers=std_headers)
    
    #Assert
    assert res.status_code == 404

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
    
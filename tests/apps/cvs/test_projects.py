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
    res = client.post("/api/cvs/project/create",
                    headers=admin_headers,
                    json={
                        "name":  testutils.random_str(3, 30),
                        "description": testutils.random_str(20, 200)
                    })
    assert res.status_code == 200

    # cleanup
    sedbackend.apps.cvs.project.implementation.delete_cvs_project(res.json()["id"], res.json()["owner"]["id"])

def test_delete_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    # Act

    res = client.delete(f'/api/cvs/project/{project.id}/delete', headers=std_headers)

    # Assert
    assert res.status_code == 200



def test_edit_cvs_project(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    #Act
    name = testutils.random_str(5,50)
    res = client.put(f'/api/cvs/project/{project.id}/edit', 
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

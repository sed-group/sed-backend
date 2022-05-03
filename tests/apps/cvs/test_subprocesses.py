import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import tests.apps.cvs.testutils as tu
import tests.testutils as testutils
import sedbackend.apps.core.users.implementation as impl_users

def test_create_subprocess(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    #Act
    res = client.post(f"/api/cvs/project/{project.id}/subprocess/create",
                    headers=std_headers,
                    json={
                        "name": testutils.random_str(5,50),
                        "parent_process_id": r.randint(1, 25),
                        "order_index": r.randint(1,50) #This probably should not work like this. Serially inserted?
                    })
    
    #Assert
    assert res.status_code == 200

    #Cleanup
    tu.delete_project_by_id(project.id, current_user.id)

def test_get_subprocess(client, std_headers, std_user):
    #setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    subprocess = tu.random_subprocess(project.id, current_user.id)

    #Act
    res = client.get(f'/api/cvs/project/{project.id}/subprocess/get/{subprocess.id}', headers=std_headers)

    #Assert
    assert res.status_code == 200
    assert subprocess.parent_process == res.json()["chunk"]["parent_process"]["id"]

    #cleanup
    tu.delete_subprocess_by_id(subprocess.id, project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_edit_subprocess(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    subprocess = tu.random_subprocess(project.id, current_user.id)

    #Act
    new_name = testutils.random_str(5, 50)
    new_parent_process = r.randint(1, 25)

    res = client.put(f'/api/cvs/project/{project.id}/subprocess/{subprocess.id}/edit',
                    headers=std_headers,
                    json={
                        "name": new_name,
                        "parent_process_id": new_parent_process
                    }) #Might break because no order_index is supplied
    
    #Assert
    assert res.status_code == 200
    assert res.json()["name"] == new_name
    assert res.json()["parent_process"]["id"] == new_parent_process

    #Cleanup
    tu.delete_subprocess_by_id(subprocess.id, project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_delete_subprocess(client, std_headers, std_user):
    #Setup 
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    subprocess = tu.random_subprocess(project.id, current_user.id)

    #Act

    res = client.delete(f'/api/cvs/project/{project.id}/subprocess/{subprocess.id}/delete', headers=std_headers)

    #Assert
    assert res.status_code == 200
    # TODO assert that it actually is gone

    #Cleanup 
    tu.delete_project_by_id(project.id, current_user.id)

def test_get_all_subprocesses(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    subprocesses = tu.seed_random_subprocesses(project.id, current_user.id, 20)
    amount_of_subprocesses = len(subprocesses)
    #Act

    res = client.get(f'/api/cvs/project/{project.id}/subprocess/get/all', headers=std_headers)

    #Assert
    assert res.status_code == 200
    assert amount_of_subprocesses == len(res.json()["chunk"])

    #cleanup
    tu.delete_subprocesses(subprocesses, project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)

def test_update_indices(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)

    subprocesses = tu.seed_random_subprocesses(project.id, current_user.id, 10)
    subprocess_ids = []
    subprocess_indices = []
    
    new_indices = []
    i = 1
    for subp in subprocesses:
        subprocess_ids.append(subp.id)
        subprocess_indices.append(subp.order_index)
        new_indices.append(i)
        i = i + 1

    #Act
    res = client.put(f'/api/cvs/project/{project.id}/subprocess/update-indices', 
                headers=std_headers,
                json={
                    "subprocess_ids": subprocess_ids,
                    "order_indices": new_indices
                })
    
    new_subp = impl.get_all_subprocess(project.id, current_user.id)
    indices = []
    for subp in new_subp.chunk:
        indices.append(subp.order_index)
    
    #Assert
    assert res.status_code == 200 
    assert indices == new_indices

    #Cleanup
    tu.delete_subprocesses(subprocesses, project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)


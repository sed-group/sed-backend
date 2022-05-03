import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import tests.apps.cvs.testutils as tu
import tests.testutils as testutils
import sedbackend.apps.core.users.implementation as impl_users

def test_create_design(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    current_project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, current_project.id)

    #Act
    res = client.post(f'/api/cvs/project/{current_project.id}/vcs/{vcs.id}/design/create', 
                    headers=std_headers,
                    json={
                        "name": testutils.random_str(5,50),
                        "description": testutils.random_str(20,200)
                    })
    
    # Assert
    assert res.status_code == 200

    #Cleanup
    tu.delete_design_by_id(res.json()["id"], current_project.id, vcs.id, current_user.id)
    tu.delete_VCS_with_ids([vcs.id],current_project.id, current_user.id)
    tu.delete_project_by_id(current_project.id, current_user.id)

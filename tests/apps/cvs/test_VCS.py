import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
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
    impl.delete_cvs_project(res.json()["id"], res.json()["user_id"])

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


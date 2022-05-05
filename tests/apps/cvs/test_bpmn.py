import random as r

import pytest
from fastapi import HTTPException

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import tests.apps.cvs.testutils as tu
import tests.testutils as testutils
import sedbackend.apps.core.users.implementation as impl_users

def test_create_bpmn_node(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, project.id)

    #Act
    res = client.post(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/bpmn/node/create',
                    headers=std_headers,
                    json={
                        "name": testutils.random_str(5,50),
                        "node_type": testutils.random_str(5,50),
                        "pos_x": r.randint(1,400),
                        "pos_y": r.randint(1,400)
                    })
    #Assert
    res.status_code == 200

    #Cleanup
    tu.delete_bpmn_node(res.json()["id"], project.id, vcs.id, current_user.id)
    tu.delete_VCS_with_ids([vcs.id], project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)


def test_get_bpmn(client, std_headers, std_user):
    #Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    project = tu.seed_random_project(current_user.id)
    vcs = tu.seed_random_vcs(current_user.id, project.id)
    bpmn_nodes = tu.seed_random_bpmn_nodes(project.id, vcs.id, current_user.id, 20)
    amount_of_bpmn_nodes = len(bpmn_nodes)
    bpmn_edges = tu.seed_random_bpmn_edges(project.id, vcs.id, current_user.id, bpmn_nodes, 6)

    #Act
    res = client.get(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/bpmn/get', headers=std_headers)
    
    #Assert
    assert res.status_code == 200
    assert len(res.json()["nodes"]) == amount_of_bpmn_nodes
    assert len(res.json()["edges"]) == len(bpmn_edges)

    #Cleanup
    tu.delete_multiple_bpmn_edges(bpmn_edges, project.id, vcs.id, current_user.id)
    tu.delete_multiple_bpmn_nodes(bpmn_nodes, project.id, vcs.id, current_user.id)
    tu.delete_VCS_with_ids([vcs.id], project.id, current_user.id)
    tu.delete_project_by_id(project.id, current_user.id)
   

def test_edit_bpmn(client, std_headers, std_user):
    #Setup
#    current_user = impl_users.impl_get_user_with_username(std_user.username)
#    project = tu.seed_random_project(current_user.id)
#    vcs = tu.seed_random_vcs(current_user.id, project.id)
#    bpmn_nodes = tu.seed_random_bpmn_nodes(project.id, vcs.id, current_user.id, 20)
#    amount_of_bpmn_nodes = len(bpmn_nodes)
#    bpmn_edges = tu.seed_random_bpmn_edges(project.id, vcs.id, current_user.id, bpmn_nodes, 6)



    #Act
#    res = client.put(f'/api/cvs/project/{project.id}/vcs/{vcs.id}/bpmn/edit',
#                    headers=std_headers,
#                    json={
#                        "nodes": bpmn_nodes,
#                        "edges": bpmn_edges
#                    })

    #Assert
#    assert res.status_code == 200

    #Cleanup
#    tu.delete_multiple_bpmn_edges(bpmn_edges, project.id, vcs.id, current_user.id)
#    tu.delete_multiple_bpmn_nodes(bpmn_nodes, project.id, vcs.id, current_user.id)
#    tu.delete_VCS_with_ids([vcs.id], project.id, current_user.id)
#    tu.delete_project_by_id(project.id, current_user.id)
    pass

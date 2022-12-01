from turtle import end_fill
from typing import List
import random

import sedbackend.apps.cvs.design.implementation
import sedbackend.apps.cvs.design.models
import sedbackend.apps.cvs.life_cycle.implementation
import sedbackend.apps.cvs.life_cycle.models
import sedbackend.apps.cvs.project.implementation
import sedbackend.apps.cvs.project.models
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.vcs.models
import tests.testutils as tu

def random_project(name: str = None, description: str=None):
    if name is None:
        name = tu.random_str(5, 50)
     
    if description is None:
        description = tu.random_str(20, 200)
    
    project = sedbackend.apps.cvs.project.models.CVSProjectPost(
        name = name,
        description = description
    )

    return project

def seed_random_project(user_id):
    p = random_project()

    new_p = sedbackend.apps.cvs.project.implementation.create_cvs_project(p, user_id)
    return new_p

def delete_project_by_id(project_id, user_id):
    sedbackend.apps.cvs.project.implementation.delete_cvs_project(project_id, user_id)

def random_VCS(name: str =None, description: str=None, year_from: int=None, year_to: int=None):
    if name is None:
        name = tu.random_str(5, 50)
    
    if description is None:
        description = tu.random_str(20, 200)
    
    if year_from is None:
        year_from = random.randint(1999, 2145)
    
    if year_to is None: 
        year_to = year_from + random.randint(5, 25)
    
    vcs = sedbackend.apps.cvs.vcs.models.VCSPost(
        name=name,
        description=description,
        year_from=year_from,
        year_to=year_to
    )

    return vcs

def seed_random_vcs(user_id, project_id):
    vcs = random_VCS()

    new_vcs = sedbackend.apps.cvs.vcs.implementation.create_vcs(vcs, project_id, user_id)

    return new_vcs

def delete_VCSs(vcs_list: List[sedbackend.apps.cvs.vcs.models.VCS], project_id, user_id):
    id_list = []
    for vcs in vcs_list:
        id_list.append(vcs.id)
    
    delete_VCS_with_ids(id_list, project_id, user_id)

def delete_VCS_with_ids(vcs_id_list: List[int], project_id: int, user_id: int):
    for vcsid in vcs_id_list:
        sedbackend.apps.cvs.vcs.implementation.delete_vcs(vcsid, project_id, user_id)


def random_value_driver(name: str=None, unit: str=None):
    if name is None:
        name = tu.random_str(5,50)
    
    return sedbackend.apps.cvs.vcs.models.VCSValueDriverPost(
        name=name
    )

def seed_random_value_driver(user_id, project_id):
    value_driver = random_value_driver()
    
    new_value_driver = sedbackend.apps.cvs.vcs.implementation.create_value_driver(value_driver, project_id, user_id)

    return new_value_driver

def delete_vd_by_id(vd_id, project_id, user_id):
    sedbackend.apps.cvs.vcs.implementation.delete_value_driver(vd_id, project_id, user_id)

def delete_vcs_table_row_by_id(table_row_id):
    print('Delete all vcs table row')

def random_table_row(project_id,
                    user_id,
                    vcs_id: int,
                    index: int = None,
                    iso_process_id: int = None,
                    subprocess_id: int= None,
                    stakeholder: str=None,
                    stakeholder_expectations: str=None,
                    stakeholder_needs: List[sedbackend.apps.cvs.vcs.models.StakeholderNeedPost] = None
                    ) -> sedbackend.apps.cvs.vcs.models.VcsRowPost:

    if index is None:
        index = random.randint(1,15)
    
   # if iso_process_id or subprocess_id is None:
   #     if iso_process_id and subprocess_id is None:
    if random.randint(1,2) == 2:
        iso_process_id = random.randint(1, 25)
    else:
        subprocess = random_subprocess(project_id, user_id )
        subprocess_id = subprocess.id

    #elif iso_process_id is not None and subprocess_id is not None:
    #    if random.randint(1,2) == 2:
    #        iso_process_id = None
    #    else:
    #        subprocess_id = None
    
    if stakeholder is None:
        stakeholder = tu.random_str(5, 50)
    
    if stakeholder_expectations is None:
        stakeholder_expectations = tu.random_str(5,50)
    
    if stakeholder_needs is None:
        stakeholder_needs = seed_stakeholder_needs(user_id, project_id)
    
    table_row = sedbackend.apps.cvs.vcs.models.VcsRowPost(
        index=index,
        iso_process_id=iso_process_id,
        subprocess_id=subprocess_id,
        stakeholder=stakeholder,
        stakeholder_expectations=stakeholder_expectations,
        stakeholder_needs=stakeholder_needs
    )

    return table_row

def random_subprocess(project_id, user_id, name: str = None, parent_process_id: int = None, order_index: int = None):
    if name is None:
        name = tu.random_str(5,50)
    if parent_process_id is None:
        parent_process_id = random.randint(1,25)
    
    subprocess = sedbackend.apps.cvs.vcs.models.VCSSubprocessPost( #TODO fix bug here. Cannot create subprocess without order_index
        name=name,
        parent_process_id=parent_process_id,
        order_index=random.randint(1,10)
    )
    subp = sedbackend.apps.cvs.vcs.implementation.create_subprocess(subprocess, project_id, user_id)
    return subp

def seed_random_subprocesses(project_id, user_id, amount = 15):
    subprocess_list = []
    while amount > 0:
        subprocess_list.append(random_subprocess(project_id, user_id))
        amount = amount - 1
    
    return subprocess_list

def delete_subprocess_by_id(subprocess_id, project_id, user_id):
    sedbackend.apps.cvs.vcs.implementation.delete_subprocess(subprocess_id, project_id, user_id)

def delete_subprocesses(subprocesses, project_id, user_id):
    for subp in subprocesses:
        delete_subprocess_by_id(subp.id, project_id, user_id)

def random_stakeholder_need(user_id,
                        project_id,
                        need: str = None,
                        rank_weight: int = None,
                        value_driver_ids: List[int]=None) -> sedbackend.apps.cvs.vcs.models.StakeholderNeedPost:
    if need is None:
        need = tu.random_str(5, 50)
    
    if rank_weight is None:
        rank_weight = random.randint(1, 100)
    
    if value_driver_ids is None:
        vd = seed_random_value_driver(user_id, project_id)
        value_driver_ids = [vd.id] #Should work....

    stakeholder_need = sedbackend.apps.cvs.vcs.models.StakeholderNeedPost(
        need=need,
        rank_weight=rank_weight,
        value_driver_ids=value_driver_ids
    )
    return stakeholder_need

def seed_stakeholder_needs(user_id, project_id, amount=10) -> List[sedbackend.apps.cvs.vcs.models.StakeholderNeedPost]:
    stakeholder_needs = []
    while amount > 0:
        stakeholder_need = random_stakeholder_need(user_id, project_id)
        stakeholder_needs.append(stakeholder_need)
        amount = amount - 1
    
    return stakeholder_needs

def seed_vcs_table_rows(vcs_id, project_id, user_id, amount=15) -> sedbackend.apps.cvs.vcs.models.VCSPost:
    table_rows =  []
    while (amount > 0):
        tr = random_table_row(project_id, user_id)
        table_rows.append(tr)
        amount = amount - 1
    
    vcs_table = vcs_impl.edit_vcs_table(table_rows, vcs_id, project_id)
    return vcs_table

def random_design(name: str = None, description: str = None):
    if name is None:
        name = tu.random_str(5,50)
    
    if description is None:
        description = tu.random_str(20,200)
    
    return sedbackend.apps.cvs.design.models.DesignPost(
        name=name,
        description=description
    )

def seed_random_designs(project_id, vcs_id, user_id, amount = 15):
    design_list = []
    while amount > 0:
        design = random_design()
        design_list.append(
            sedbackend.apps.cvs.design.implementation.create_cvs_design(design, vcs_id, project_id, user_id))
        amount = amount - 1

    return design_list

def delete_designs(designs, project_id, vcs_id, user_id):
    for design in designs:
        delete_design_by_id(design.id, project_id, vcs_id, user_id)

def delete_design_by_id(design_id, project_id, vcs_id, user_id):
    sedbackend.apps.cvs.design.implementation.delete_design(design_id, vcs_id, project_id, user_id)

def random_quantified_objective(name: str =None, property: float =None, unit: str=None):
    if name is None:
        name = tu.random_str(5,50)
    
    if property is None:
        property = random.uniform(0.5, 100)
    
    if unit is None: 
        unit = tu.random_str(5,50)
    
    return sedbackend.apps.cvs.design.models.QuantifiedObjectivePost(
        name=name,
        property=property,
        unit=unit
    )

def seed_random_quantified_objectives(project_id, vcs_id, design_id, user_id, amount = 15):
    quantified_objectives = []
    while amount > 0:
        vd = seed_random_value_driver(user_id, project_id)
        qo = random_quantified_objective()
        quantified_objectives.append(
            sedbackend.apps.cvs.design.implementation.create_quantified_objective(design_id, vd.id, qo, project_id, vcs_id, user_id))
        amount = amount - 1
    
    return quantified_objectives

def delete_qo_and_vd(qo_id, vd_id, project_id, vcs_id, design_id, user_id):
    sedbackend.apps.cvs.design.implementation.delete_quantified_objective(qo_id, vd_id, design_id, project_id, vcs_id, user_id)
    sedbackend.apps.cvs.vcs.implementation.delete_value_driver(vd_id, project_id, user_id)

def delete_quantified_objectives(quantified_objectives, project_id, vcs_id, design_id, user_id):
    for qo in quantified_objectives:
        delete_qo_and_vd(qo.id, qo.value_driver.id, project_id, vcs_id, design_id, user_id)

# ======================================================================================================================
# BPMN Table
# ======================================================================================================================

def random_node(name: str = None, node_type: str = None, pos_x: int = None, pos_y: int = None):
    if name is None:
        name = tu.random_str(5,50)
    if node_type is None:
        if random.randint(1,2) == 2:
            node_type = tu.random_str(5,50)
        else:
            node_type = "process"
    if pos_x is None:
        pos_x = random.randint(1, 400)
    if pos_y is None:
        pos_y = random.randint(1, 400)
    
    return sedbackend.apps.cvs.life_cycle.models.NodePost(
        name=name,
        node_type=node_type,
        pos_x=pos_x,
        pos_y=pos_y
    )

def random_edge(from_node: int, to_node: int, name: str = None, probability: int = None):
    if name is None:
        name = tu.random_str(5, 50)
    
    if probability is None:
        probability = 1
    
    return sedbackend.apps.cvs.life_cycle.models.EdgePost(
        name=name,
        from_node=from_node,
        to_node=to_node,
        probability=probability
    )

def seed_random_bpmn_edges(project_id, vcs_id, user_id, bpmn_nodes, amount = 15):
    bpmn_edges = []
    outgoing_nodes = bpmn_nodes
    incoming_nodes = bpmn_nodes

    while amount > 0:
        from_node = outgoing_nodes.pop(random.randint(0, len(outgoing_nodes) - 1))
        to_node = incoming_nodes.pop(random.randint(0, len(incoming_nodes) - 1))

        new_edge = random_edge(from_node.id, to_node.id)
        bpmn_edges.append(
            sedbackend.apps.cvs.life_cycle.implementation.create_bpmn_edge(new_edge, project_id, vcs_id, user_id))
        amount = amount - 1
    return bpmn_edges

def seed_random_bpmn_nodes(project_id, vcs_id, user_id, amount = 15):
    bpmn_nodes = []
    while amount > 0:
        node = random_node()
        bpmn_nodes.append(
            sedbackend.apps.cvs.life_cycle.implementation.create_bpmn_node(node, project_id, vcs_id, user_id))
        amount = amount - 1
    return bpmn_nodes

def delete_bpmn_node(node_id, project_id, vcs_id, user_id):
    sedbackend.apps.cvs.life_cycle.implementation.delete_bpmn_node(node_id, project_id, vcs_id, user_id)

def delete_bpmn_edge(edge_id, project_id, vcs_id, user_id):
    sedbackend.apps.cvs.life_cycle.implementation.delete_bpmn_edge(edge_id, project_id, vcs_id, user_id)

def delete_multiple_bpmn_edges(edges, project_id, vcs_id, user_id):
    for edge in edges:
        delete_bpmn_edge(edge.id, project_id, vcs_id, user_id)

def delete_multiple_bpmn_nodes(nodes, project_id, vcs_id, user_id):
    for node in nodes:
        delete_bpmn_node(node.id, project_id, vcs_id, user_id)
from decimal import Decimal
from turtle import end_fill
from typing import List, Tuple
import random

import sedbackend.apps.cvs.design.implementation as design_impl
import sedbackend.apps.cvs.design.models as design_model
import sedbackend.apps.cvs.link_design_lifecycle.implementation as connect_impl
import sedbackend.apps.cvs.link_design_lifecycle.models as connect_model
import sedbackend.apps.cvs.life_cycle.implementation
import sedbackend.apps.cvs.life_cycle.models
import sedbackend.apps.cvs.project.implementation
import sedbackend.apps.cvs.project.models
import sedbackend.apps.cvs.vcs.implementation as vcs_impl
import sedbackend.apps.cvs.vcs.models as vcs_model
from sedbackend.apps.cvs.link_design_lifecycle.models import TimeFormat, Rate
import tests.testutils as tu


# ======================================================================================================================
# Project
# ======================================================================================================================


def random_project(name: str = None, description: str = None):
    if name is None:
        name = tu.random_str(5, 50)

    if description is None:
        description = tu.random_str(20, 200)

    project = sedbackend.apps.cvs.project.models.CVSProjectPost(
        name=name,
        description=description
    )

    return project


def seed_random_project(user_id):
    p = random_project()

    new_p = sedbackend.apps.cvs.project.implementation.create_cvs_project(
        p, user_id)
    return new_p


def delete_project_by_id(project_id, user_id):
    sedbackend.apps.cvs.project.implementation.delete_cvs_project(
        project_id, user_id)


# ======================================================================================================================
# VCS
# ======================================================================================================================


def random_VCS(name: str = None, description: str = None, year_from: int = None, year_to: int = None):
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


def seed_random_vcs(project_id):
    vcs = random_VCS()

    new_vcs = vcs_impl.create_vcs(project_id, vcs)

    return new_vcs


def delete_VCSs(project_id: int, vcs_list: List[sedbackend.apps.cvs.vcs.models.VCS]):
    id_list = []
    for vcs in vcs_list:
        id_list.append(vcs.id)

    delete_VCS_with_ids(project_id, id_list)


def delete_VCS_with_ids(project_id: int, vcs_id_list: List[int]):
    for vcsid in vcs_id_list:
        vcs_impl.delete_vcs(project_id, vcsid)


def random_value_driver(name: str = None):
    if name is None:
        name = tu.random_str(5, 50)

    return sedbackend.apps.cvs.vcs.models.ValueDriverPost(
        name=name
    )


def seed_random_value_driver(user_id):
    value_driver = random_value_driver()

    new_value_driver = sedbackend.apps.cvs.vcs.implementation.create_value_driver(
        user_id, value_driver)

    return new_value_driver


def delete_vd_by_id(vd_id):
    sedbackend.apps.cvs.vcs.implementation.delete_value_driver(vd_id)


def delete_vd_from_user(user_id):
    sedbackend.apps.cvs.vcs.implementation.delete_all_value_drivers(user_id)


def delete_vcs_table_row_by_id(table_row_id):
    print('Delete all vcs table row')


def random_table_row(
        user_id: int,
        vcs_id: int,
        index: int = None,
        iso_process_id: int = None,
        subprocess_id: int = None,
        stakeholder: str = None,
        stakeholder_expectations: str = None,
        stakeholder_needs: List[sedbackend.apps.cvs.vcs.models.StakeholderNeedPost] = None
) -> sedbackend.apps.cvs.vcs.models.VcsRowPost:
    if index is None:
        index = random.randint(1, 15)

    if random.randint(1, 2) == 2:
        iso_process_id = random.randint(1, 25)
    else:
        subprocess = random_subprocess(vcs_id, user_id)
        subprocess_id = subprocess.id

    if stakeholder is None:
        stakeholder = tu.random_str(5, 50)

    if stakeholder_expectations is None:
        stakeholder_expectations = tu.random_str(5, 50)

    if stakeholder_needs is None:
        stakeholder_needs = seed_stakeholder_needs(user_id)

    table_row = sedbackend.apps.cvs.vcs.models.VcsRowPost(
        index=index,
        iso_process=iso_process_id,
        subprocess=subprocess_id,
        stakeholder=stakeholder,
        stakeholder_expectations=stakeholder_expectations,
        stakeholder_needs=stakeholder_needs
    )

    return table_row


def random_subprocess(vcs_id, user_id, name: str = None, parent_process_id: int = None, order_index: int = None):
    if name is None:
        name = tu.random_str(5, 50)
    if parent_process_id is None:
        parent_process_id = random.randint(1, 25)

    subprocess = sedbackend.apps.cvs.vcs.models.VCSSubprocessPost(
        # TODO fix bug here. Cannot create subprocess without order_index
        name=name,
        parent_process_id=parent_process_id,
        order_index=random.randint(1, 10)
    )
    subp = sedbackend.apps.cvs.vcs.implementation.create_subprocess(
        vcs_id, subprocess)
    return subp


def seed_random_subprocesses(project_id, user_id, amount=15):
    subprocess_list = []
    while amount > 0:
        subprocess_list.append(random_subprocess(project_id, user_id))
        amount = amount - 1

    return subprocess_list


def delete_subprocess_by_id(subprocess_id, project_id, user_id):
    sedbackend.apps.cvs.vcs.implementation.delete_subprocess(
        subprocess_id, project_id, user_id)


def delete_subprocesses(subprocesses, project_id, user_id):
    for subp in subprocesses:
        delete_subprocess_by_id(subp.id, project_id, user_id)


def random_stakeholder_need(user_id,
                            need: str = None,
                            rank_weight: float = None,
                            value_driver_ids: List[int] = None) -> sedbackend.apps.cvs.vcs.models.StakeholderNeedPost:
    if need is None:
        need = tu.random_str(5, 50)

    if rank_weight is None:
        rank_weight = random.random()

    if value_driver_ids is None:
        vd = seed_random_value_driver(user_id)
        value_driver_ids = [vd.id]  # Should work....

    stakeholder_need = sedbackend.apps.cvs.vcs.models.StakeholderNeedPost(
        need=need,
        rank_weight=rank_weight,
        value_driver_ids=value_driver_ids
    )
    return stakeholder_need


def seed_stakeholder_needs(user_id, amount=10) -> List[sedbackend.apps.cvs.vcs.models.StakeholderNeedPost]:
    stakeholder_needs = []
    for _ in range(amount):
        stakeholder_need = random_stakeholder_need(user_id)
        stakeholder_needs.append(stakeholder_need)

    return stakeholder_needs


def seed_vcs_table_rows(user_id, project_id, vcs_id, amount=15) -> List[vcs_model.VcsRow]:
    table_rows = []
    for _ in range(amount):
        tr = random_table_row(user_id, vcs_id)
        table_rows.append(tr)

    vcs_impl.edit_vcs_table(project_id, vcs_id, table_rows)
    table = vcs_impl.get_vcs_table(project_id, vcs_id)

    return table


# ======================================================================================================================
# BPMN Table
# ======================================================================================================================

def random_node(name: str = None, node_type: str = None, pos_x: int = None, pos_y: int = None):
    if name is None:
        name = tu.random_str(5, 50)
    if node_type is None:
        if random.randint(1, 2) == 2:
            node_type = tu.random_str(5, 50)
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


def seed_random_bpmn_edges(project_id, vcs_id, user_id, bpmn_nodes, amount=15):
    bpmn_edges = []
    outgoing_nodes = bpmn_nodes
    incoming_nodes = bpmn_nodes

    while amount > 0:
        from_node = outgoing_nodes.pop(
            random.randint(0, len(outgoing_nodes) - 1))
        to_node = incoming_nodes.pop(
            random.randint(0, len(incoming_nodes) - 1))

        new_edge = random_edge(from_node.id, to_node.id)
        bpmn_edges.append(
            sedbackend.apps.cvs.life_cycle.implementation.create_bpmn_edge(new_edge, project_id, vcs_id, user_id))
        amount = amount - 1
    return bpmn_edges


def seed_random_bpmn_nodes(project_id, vcs_id, user_id, amount=15):
    bpmn_nodes = []
    while amount > 0:
        node = random_node()
        bpmn_nodes.append(
            sedbackend.apps.cvs.life_cycle.implementation.create_bpmn_node(node, project_id, vcs_id, user_id))
        amount = amount - 1
    return bpmn_nodes


def delete_bpmn_node(node_id, project_id, vcs_id, user_id):
    sedbackend.apps.cvs.life_cycle.implementation.delete_bpmn_node(
        node_id, project_id, vcs_id, user_id)


def delete_bpmn_edge(edge_id, project_id, vcs_id, user_id):
    sedbackend.apps.cvs.life_cycle.implementation.delete_bpmn_edge(
        edge_id, project_id, vcs_id, user_id)


def delete_multiple_bpmn_edges(edges, project_id, vcs_id, user_id):
    for edge in edges:
        delete_bpmn_edge(edge.id, project_id, vcs_id, user_id)


def delete_multiple_bpmn_nodes(nodes, project_id, vcs_id, user_id):
    for node in nodes:
        delete_bpmn_node(node.id, project_id, vcs_id, user_id)


# ======================================================================================================================
# Designs
# ======================================================================================================================


def seed_random_design_group(project_id: int, name: str = None, vcs_id: int = None):
    """
    If a vcs_id is specified, the backend will pull all value drivers from that VCS
    and put it in this design group.
    """
    if name is None:
        name = tu.random_str(5, 50)

    design_group_post = design_model.DesignGroupPost(
        name=name,
        vcs_id=vcs_id
    )

    dg = design_impl.create_cvs_design_group(design_group_post, project_id)

    return dg


def delete_design_group(project_id: int, dg_id: int):
    design_impl.delete_design_group(project_id, dg_id)


# ======================================================================================================================
# Connect design to lifecycle (Formulas)
# ======================================================================================================================

def seed_random_formulas(project_id: int, vcs_id: int, design_group_id: int, user_id: int, amount: int = 10) -> List[
    connect_model.FormulaRowGet]:
    for _ in range(amount):
        vcs_row = seed_vcs_table_rows(vcs_id, project_id, user_id, 1)

        time = tu.random_str(10, 200)
        time_unit = random_time_unit()
        cost = tu.random_str(10, 200)
        revenue = tu.random_str(10, 200)
        rate = random_rate_choice()

        # TODO when value drivers and market inputs are connected to the
        # formulas, add them here.
        value_driver_ids = []
        market_input_ids = []

        formulaPost = connect_model.FormulaPost(
            time=time,
            time_unit=time_unit,
            cost=cost,
            revenue=revenue,
            rate=rate,
            value_driver_ids=value_driver_ids,
            market_input_ids=market_input_ids
        )

        connect_impl.edit_formulas(project_id, vcs_row[0].id, design_group_id, formulaPost)

    return connect_impl.get_all_formulas(project_id, vcs_id, design_group_id)


def delete_formulas(project_id: int, vcsRow_Dg_ids: List[Tuple[int, int]]):
    for (vcs_row, dg) in vcsRow_Dg_ids:
        connect_impl.delete_formulas(project_id, vcs_row, dg)


# ======================================================================================================================
# Utility
# ======================================================================================================================

def random_time_unit():
    return random.choice(list(TimeFormat)).value


def random_rate_choice():
    return random.choice(list(Rate)).value

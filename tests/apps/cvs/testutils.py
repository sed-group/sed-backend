from typing import List, Tuple, Optional
from typing import List, Tuple
import random

import sedbackend.apps.cvs.simulation.implementation as sim_impl
import sedbackend.apps.cvs.simulation.models as sim_model
from sedbackend.apps.cvs.simulation.models import NonTechCost
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
from sedbackend.apps.cvs.link_design_lifecycle.models import FormulaGet, FormulaRowGet, TimeFormat, Rate
from sedbackend.apps.cvs.market_input import models as market_input_model, implementation as market_input_impl
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


def random_value_driver(name: str = None, unit: str = None):
    if name is None:
        name = tu.random_str(5, 50)
    if unit is None:
        unit = tu.random_str(0, 10)

    return sedbackend.apps.cvs.vcs.models.ValueDriverPost(
        name=name,
        unit=unit
    )


def seed_random_value_driver(user_id) -> sedbackend.apps.cvs.vcs.models.ValueDriver:
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
        project_id: int,
        vcs_id: int,
        index: Optional[int] = None,
        iso_process_id: Optional[int] = None,
        subprocess_id: Optional[int] = None,
        stakeholder: Optional[str] = None,
        stakeholder_expectations: Optional[str] = None,
        stakeholder_needs: List[vcs_model.StakeholderNeedPost] = None
) -> vcs_model.VcsRowPost:
    if index is None:
        index = random.randint(1, 15)

    if random.randint(1, 8) == 2:
        subprocess = random_subprocess(project_id, vcs_id)
        subprocess_id = subprocess.id
    else:
        iso_process_id = random.randint(1, 25)

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


def random_subprocess(project_id: int, vcs_id: int, name: str = None, parent_process_id: int = None):
    if name is None:
        name = tu.random_str(5, 50)
    if parent_process_id is None:
        parent_process_id = random.randint(1, 25)

    subprocess = vcs_model.VCSSubprocessPost(
        name=name,
        parent_process_id=parent_process_id
    )
    subp = vcs_impl.create_subprocess(project_id, vcs_id, subprocess)
    return subp


def seed_random_subprocesses(project_id: int, vcs_id: int, amount=15):
    subprocess_list = []
    for _ in range(amount):
        subprocess_list.append(random_subprocess(project_id, vcs_id))

    return subprocess_list


def delete_subprocess_by_id(subprocess_id, project_id):
    vcs_impl.delete_subprocess(
        subprocess_id, project_id)


def delete_subprocesses(subprocesses, project_id):
    for subp in subprocesses:
        delete_subprocess_by_id(subp.id, project_id)


def random_stakeholder_need(user_id,
                            need: str = None,
                            rank_weight: float = None,
                            value_driver_ids: List[int] = None) -> sedbackend.apps.cvs.vcs.models.StakeholderNeedPost:
    if need is None:
        need = tu.random_str(5, 50)

    if rank_weight is None:
        rank_weight = round(random.random(), ndigits=4)

    if value_driver_ids is None:
        vd = seed_random_value_driver(user_id)
        value_driver_ids = [vd.id]

    stakeholder_need = sedbackend.apps.cvs.vcs.models.StakeholderNeedPost(
        need=need,
        rank_weight=rank_weight,
        value_drivers=value_driver_ids
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
        tr = random_table_row(user_id, project_id, vcs_id)
        table_rows.append(tr)

    vcs_impl.edit_vcs_table(project_id, vcs_id, table_rows)
    table = vcs_impl.get_vcs_table(project_id, vcs_id)

    return table


def create_vcs_table(project_id, vcs_id, rows: List[vcs_model.VcsRowPost]) -> List[vcs_model.VcsRow]:
    vcs_impl.edit_vcs_table(project_id, vcs_id, rows)
    return vcs_impl.get_vcs_table(project_id, vcs_id)

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

    dg = design_impl.create_cvs_design_group(project_id, design_group_post)

    return dg


def delete_design_group(project_id: int, dg_id: int):
    design_impl.delete_design_group(project_id, dg_id)


def random_design(value_driver_ids: int = None):
    name = tu.random_str(5, 50)
    vd_design_values = []
    if value_driver_ids is None:
        vd_design_values = []
    else:
        for vd_id in value_driver_ids:
            designValue = design_model.ValueDriverDesignValue(
                vd_id=vd_id,
                value=round(tu.random.uniform(1, 400), ndigits=5)
            )
            vd_design_values.append(designValue)

    return design_model.DesignPut(
        name=name,
        vd_design_values=vd_design_values
    )


def seed_random_designs(project_id: int, dg_id: int, amount: int = 10):

    design_impl.edit_designs(project_id, dg_id, [design_model.DesignPut(name=tu.random_str(5, 50))
                                                 for _ in range(amount)])

    return design_impl.get_all_designs(project_id, dg_id)


# ======================================================================================================================
# Connect design to lifecycle (Formulas)
# ======================================================================================================================

def seed_random_formulas(project_id: int, vcs_id: int, design_group_id: int, user_id: int, amount: int = 10) -> List[connect_model.FormulaRowGet]:
    vcs_rows = seed_vcs_table_rows(user_id,  project_id, vcs_id, amount)
    rate_per_prod = False
    for vcs_row in vcs_rows:

        time = str(tu.random.randint(1, 200))
        time_unit = random_time_unit()
        cost = str(tu.random.randint(1, 2000))
        revenue = str(tu.random.randint(1, 10000))
        rate = random_rate_choice()
        if rate == Rate.PRODUCT.value:
            rate_per_prod = True
        if rate_per_prod and rate == Rate.PROJECT.value:
            rate = Rate.PRODUCT.value

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

        connect_impl.edit_formulas(
            project_id, vcs_row.id, design_group_id, formulaPost)

    return connect_impl.get_all_formulas(project_id, vcs_id, design_group_id)


def create_formulas(project_id: int, vcs_rows: List[vcs_model.VcsRow], dg_id: int) -> List[FormulaRowGet]:
    for row in vcs_rows:
        time = str(tu.random.randint(1, 200))
        time_unit = random_time_unit()
        cost = str(tu.random.randint(1, 2000))
        revenue = str(tu.random.randint(1, 10000))
        rate = Rate.PRODUCT.value

        formulaPost = connect_model.FormulaPost(
            time=time,
            time_unit=time_unit,
            cost=cost,
            revenue=revenue,
            rate=rate,
            value_driver_ids=[],
            market_input_ids=[]
        )
        connect_impl.edit_formulas(project_id, row.id, dg_id, formulaPost)

    return connect_impl.get_all_formulas(project_id, vcs_rows[0].vcs_id, dg_id)


def delete_formulas(project_id: int, vcsRow_Dg_ids: List[Tuple[int, int]]):
    for (vcs_row, dg) in vcsRow_Dg_ids:
        connect_impl.delete_formulas(project_id, vcs_row, dg)


def seed_formulas_for_multiple_vcs(project_id: int, vcss: List[int], dgs: List[int], user_id: int):
    tr = random_table_row(user_id, project_id, vcss[0])
    while tr.subprocess != None:
        tr = random_table_row(user_id, project_id,  vcss[0])

    row_ids = []
    for vcs_id in vcss:
        orig_table = vcs_impl.get_vcs_table(project_id, vcs_id)
        table = [
            vcs_model.VcsRowPost(
                id=tr.id,
                index=tr.index,
                stakeholder=tr.stakeholder,
                stakeholder_needs=[
                    vcs_model.StakeholderNeedPost(
                        id=need.id,
                        need=need.need,
                        value_dimension=need.value_dimension,
                        rank_weight=need.rank_weight,
                        value_drivers=[vd.id for vd in need.value_drivers])
                    for need in tr.stakeholder_needs],
                stakeholder_expectations=tr.stakeholder_expectations,
                iso_process=None if tr.iso_process is None else tr.iso_process.id,
                subprocess=None if tr.subprocess is None else tr.subprocess.id)
            for tr in orig_table]
        table.append(tr)
        vcs_impl.edit_vcs_table(project_id, vcs_id, table)
        row = list(filter(lambda row: row not in orig_table,
                   vcs_impl.get_vcs_table(project_id, vcs_id)))[0]
        row_ids.append(row.id)

    time = str(tu.random.randint(1, 200))
    time_unit = random_time_unit()
    cost = str(tu.random.randint(1, 2000))
    revenue = str(tu.random.randint(1, 10000))
    rate = Rate.PRODUCT.value

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

    for row_id in row_ids:
        for dg_id in dgs:
            connect_impl.edit_formulas(project_id, row_id, dg_id, formulaPost)


def edit_rate_order_formulas(project_id: int, vcs_id: int, design_group_id: int) -> vcs_model.VcsRow:
    rows = list(sorted(vcs_impl.get_vcs_table(
        project_id, vcs_id), key=lambda row: row.index))
    formulas = connect_impl.get_all_formulas(
        project_id, vcs_id, design_group_id)

    rows.reverse()  # Reverse to find last technical process
    for row in rows:
        if row.iso_process is not None:
            if row.iso_process.category == 'Technical processes':
                last_id = row.id
                break
        else:
            if row.subprocess.parent_process.category == 'Technical processes':
                last_id = row.id
                break

    last = next(filter(lambda x: x.vcs_row_id == last_id, formulas))

    new_last = connect_model.FormulaPost(
        time=last.time,
        time_unit=last.time_unit,
        cost=last.cost,
        revenue=last.revenue,
        rate=Rate.PROJECT.value,
        value_driver_ids=[vd.id for vd in last.value_drivers],
        market_input_ids=[mi.id for mi in last.market_inputs]
    )

    connect_impl.edit_formulas(project_id, last_id, design_group_id, new_last)

    rows.reverse()  # reverse back to find first technical process
    for row in rows:
        if row.iso_process is not None:
            if row.iso_process.category == 'Technical processes':
                return row
        else:
            if row.subprocess.parent_process.category == 'Technical processes':
                return row


# ======================================================================================================================
# Simulation
# ======================================================================================================================

def seed_simulation_settings(project_id: int, vcs_ids: List[int], design_ids: List[int]) -> sim_model.SimSettings:
    rows = [row.iso_process.name if row.iso_process is not None else row.subprocess.name for row in vcs_impl.get_vcs_table(
        project_id, vcs_ids[0])]
    print("Seed settings vcs rows", rows)
    for vcs_id in vcs_ids:
        new_rows = [row.iso_process.name if row.iso_process is not None else row.subprocess.name for row in vcs_impl.get_vcs_table(
            project_id, vcs_id)]
        print("New rows", new_rows)
        rows = list(filter(lambda x: x in rows, new_rows))
        print("Common elements", rows)

    time_unit = random_time_unit()
    interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
    start_time = round(tu.random.uniform(1, 300), ndigits=5)
    end_time = round(tu.random.uniform(300, 1000), ndigits=5)
    print("Row len", len(rows))
    flow_process = tu.random.choice(rows)
    flow_start_time = None  # Get valid start time
    flow_time = round(tu.random.uniform(0, end_time - start_time), ndigits=5)

    discount_rate = round(tu.random.random(), ndigits=5)
    non_tech_add = random_non_technical_cost()
    monte_carlo = bool(tu.random.getrandbits(1))
    runs = 0 if not monte_carlo else tu.random.randint(1, 200)

    sim_settings = sim_model.EditSimSettings(
        time_unit=time_unit,
        flow_process=flow_process,
        flow_start_time=flow_start_time,
        flow_time=flow_time,
        interarrival_time=interarrival_time,
        start_time=start_time,
        end_time=end_time,
        discount_rate=discount_rate,
        non_tech_add=non_tech_add,
        monte_carlo=monte_carlo,
        runs=runs
    )

    return sim_settings


def seed_random_sim_settings(user_id: int, project_id: int) -> sim_model.SimSettings:
    time_unit = random_time_unit()
    interarrival_time = round(tu.random.uniform(1, 255), ndigits=5)
    start_time = round(tu.random.uniform(1, 300), ndigits=5)
    end_time = round(tu.random.uniform(300, 1000), ndigits=5)
    if tu.random.getrandbits(1):
        vcs = seed_random_vcs(project_id)
        rows = seed_vcs_table_rows(user_id, project_id, vcs.id, 3)
        for row in rows:
            if row.subprocess is not None:
                flow_process = row.subprocess.name
                break
            elif row.iso_process is not None:
                flow_process = row.iso_process.name
                break
        flow_start_time = None  # Get valid start time
        flow_time = round(tu.random.uniform(
            0, end_time - start_time), ndigits=5)
    else:
        flow_process = None
        flow_start_time = round(tu.random.uniform(
            start_time, end_time), ndigits=5)
        flow_time = round(tu.random.uniform(
            0, end_time - flow_start_time), ndigits=5)

    discount_rate = round(tu.random.random(), ndigits=5)
    non_tech_add = random_non_technical_cost()
    monte_carlo = bool(tu.random.getrandbits(1))
    runs = 0 if not monte_carlo else tu.random.randint(1, 200)

    sim_settings = sim_model.EditSimSettings(
        time_unit=time_unit,
        flow_process=flow_process,
        flow_start_time=flow_start_time,
        flow_time=flow_time,
        interarrival_time=interarrival_time,
        start_time=start_time,
        end_time=end_time,
        discount_rate=discount_rate,
        non_tech_add=non_tech_add,
        monte_carlo=monte_carlo,
        runs=runs
    )

    sim_impl.edit_sim_settings(project_id, sim_settings)
    return sim_impl.get_sim_settings(project_id)


# ======================================================================================================================
# Market Input
# ======================================================================================================================

def seed_random_market_input(project_id: int):
    name = tu.random_str(5, 50)
    unit = tu.random_str(5, 50)
    market_input_post = market_input_model.MarketInputPost(
        name=name,
        unit=unit
    )
    return market_input_impl.create_market_input(project_id, market_input_post)


def seed_random_market_input_values(project_id: int, vcs_id: int, market_input_id: int):
    market_input_impl.update_market_input_values(project_id, [market_input_model.MarketInputValue(
        vcs_id=vcs_id,
        market_input_id=market_input_id,
        value=random.random() * 100)])

    return market_input_impl.get_all_market_values(project_id)


# ======================================================================================================================
# Utility
# ======================================================================================================================

def random_time_unit():
    return random.choice(list(TimeFormat)).value


def random_rate_choice():
    return random.choice(list(Rate)).value


def random_non_technical_cost():
    return random.choice(list(NonTechCost)).value

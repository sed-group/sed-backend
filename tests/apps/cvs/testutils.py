from turtle import end_fill
from typing import List
import random

import sedbackend.apps.cvs.implementation as impl
import sedbackend.apps.cvs.models as models
import tests.testutils as tu

def random_project(name: str = None, description: str=None):
    if name is None:
        name = tu.random_str(5, 50)
     
    if description is None:
        description = tu.random_str(20, 200)
    
    project = models.CVSProjectPost(
        name = name,
        description = description
    )

    return project

def seed_random_project(user_id):
    p = random_project()

    new_p = impl.create_cvs_project(p, user_id)
    return new_p

def delete_project_by_id(project_id, user_id):
    impl.delete_cvs_project(project_id, user_id)

def random_VCS(name: str =None, description: str=None, year_from: int=None, year_to: int=None):
    if name is None:
        name = tu.random_str(5, 50)
    
    if description is None:
        description = tu.random_str(20, 200)
    
    if year_from is None:
        year_from = random.randint(1999, 2145)
    
    if year_to is None: 
        year_to = year_from + random.randint(5, 25)
    
    vcs = models.VCSPost(
        name=name,
        description=description,
        year_from=year_from,
        year_to=year_to
    )

    return vcs

def seed_random_vcs(user_id, project_id):
    vcs = random_VCS()

    new_vcs = impl.create_vcs(vcs, project_id, user_id)

    return new_vcs

def delete_VCSs(vcs_list: List[models.VCS], project_id, user_id):
    id_list = []
    for vcs in vcs_list:
        id_list.append(vcs.id)
    
    delete_VCS_with_ids(id_list, project_id, user_id)

def delete_VCS_with_ids(vcs_id_list: List[int], project_id: int, user_id: int):
    for vcsid in vcs_id_list:
        impl.delete_vcs(vcsid, project_id, user_id)


def random_value_driver(name: str=None, unit: str=None):
    if name is None:
        name = tu.random_str(5,50)
    
    return models.VCSValueDriverPost(
        name=name
    )

def seed_random_value_driver(user_id, project_id):
    value_driver = random_value_driver()
    
    new_value_driver = impl.create_value_driver(value_driver, project_id, user_id)

    return new_value_driver

def delete_vd_by_id(vd_id, project_id, user_id):
    impl.delete_value_driver(vd_id, project_id, user_id)

def delete_vcs_table_row_by_id(table_row_id):
    print('Delete all vcs table row')

def random_table_row(project_id,
                    user_id,
                    node_id: int = None,
                    row_index: int = None,
                    iso_process_id: int = None,
                    subprocess_id: int= None,
                    stakeholder: str=None,
                    stakeholder_expectations: str=None,
                    stakeholder_needs: List[models.StakeholderNeedPost] = None
                    ) -> models.TableRowPost:
    if node_id is None: #This will break everything since after the first iteration it will have a node id
        node_id = None
    
    if row_index is None:
        row_index = random.randint(1,15)
    
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
    
    table_row = models.TableRowPost(
        node_id=node_id,
        row_index=row_index,
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
    
    subprocess = models.VCSSubprocessPost( #TODO fix bug here. Cannot create subprocess without order_index
        name=name,
        parent_process_id=parent_process_id,
        order_index=random.randint(1,10)
    )
    subp = impl.create_subprocess(subprocess, project_id, user_id)
    return subp

def random_stakeholder_need(user_id,
                        project_id,
                        need: str = None,
                        rank_weight: int = None,
                        value_driver_ids: List[int]=None) -> models.StakeholderNeedPost:
    if need is None:
        need = tu.random_str(5, 50)
    
    if rank_weight is None:
        rank_weight = random.randint(1, 100)
    
    if value_driver_ids is None:
        vd = seed_random_value_driver(user_id, project_id)
        value_driver_ids = [vd.id] #Should work....

    stakeholder_need = models.StakeholderNeedPost(
        need=need,
        rank_weight=rank_weight,
        value_driver_ids=value_driver_ids
    )
    return stakeholder_need

def seed_stakeholder_needs(user_id, project_id, amount=10) -> List[models.StakeholderNeedPost]:
    stakeholder_needs = []
    while amount > 0:
        stakeholder_need = random_stakeholder_need(user_id, project_id)
        stakeholder_needs.append(stakeholder_need)
        amount = amount - 1
    
    return stakeholder_needs

def seed_vcs_table_rows(vcs_id, project_id, user_id, amount=15) -> models.TablePost:
    table_rows =  []
    while (amount > 0):
    
        tr = random_table_row(project_id, user_id)
        table_rows.append(tr)
        amount = amount - 1
    
    table_model = models.TablePost(
        table_rows=table_rows
    )
    vcs_table = impl.create_vcs_table(table_model, vcs_id, project_id, user_id)
    return table_model


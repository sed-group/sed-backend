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
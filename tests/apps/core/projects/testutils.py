from typing import List, Dict, Optional
import random

import tests.testutils as tu
import sedbackend.apps.core.projects.models as models
import sedbackend.apps.core.projects.implementation as impl


def random_project(admin_id_list: List = None,
                   editor_id_list: List = None,
                   readonly_id_list: List = None,
                   name: str = None):

    if name is None:
        name = tu.random_str(5, 50)

    participants = []
    participants_access = {}

    if admin_id_list is not None:
        for uid in admin_id_list:
            participants.append(uid)
            participants_access[uid] = models.AccessLevel.ADMIN

    if editor_id_list is not None:
        for uid in editor_id_list:
            participants.append(uid)
            participants_access[uid] = models.AccessLevel.EDITOR

    if readonly_id_list is not None:
        for uid in readonly_id_list:
            participants.append(uid)
            participants_access[uid] = models.AccessLevel.READONLY

    project = models.ProjectPost(
        name=name,
        participants=participants,
        participants_access=participants_access
    )

    return project


def seed_random_projects(owner_id, amount=10) -> List[models.Project]:
    project_list = []
    for i in range(0, amount):
        p = random_project()
        project_list.append(impl.impl_post_project(p, owner_id))

    return project_list


def seed_random_project(owner_id: int, participants: Dict[int, models.AccessLevel] = None):
    p = random_project()

    if participants is not None:
        for participant_id in participants.keys():
            p.participants.append(participant_id)

        p.participants_access = participants

    new_p = impl.impl_post_project(p, owner_id)
    return new_p


def delete_projects(projects_list: List[models.Project]):
    id_list = []
    for p in projects_list:
        id_list.append(p.id)

    delete_projects_with_ids(id_list)


def delete_projects_with_ids(project_id_list: List[int]):
    for pid in project_id_list:
        impl.impl_delete_project(pid)
    return


def random_subproject_post():
    spp = models.SubProjectPost(
        application_sid="MOD.EFM",
        native_project_id=random.randint(0, 100000)
    )
    return spp


def seed_random_subproject(owner_id: int, project_id: Optional[int] = None):
    sp_post = random_subproject_post()
    sp = impl.impl_post_subproject(sp_post, owner_id, project_id=project_id)
    return sp


def delete_subprojects(subprojects: List[models.SubProject]):
    for sp in subprojects:
        impl.impl_delete_subproject(sp.project_id, sp.id)

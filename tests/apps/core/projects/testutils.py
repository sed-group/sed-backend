from typing import List, Dict

import tests.testutils as tu
import apps.core.projects.models as models
import apps.core.projects.implementation as impl


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


def seed_random_project(owner_id, participants: Dict[int, models.AccessLevel] = None):
    p = random_project()

    if participants is not None:
        for participant_id in participants.keys():
            p.participants.append(participant_id)

        p.participants_access = participants

    new_p = impl.impl_post_project(p, owner_id)
    return new_p


def delete_projects(projects_list):
    id_list = []
    for p in projects_list:
        id_list.append(p.id)

    delete_projects_with_ids(id_list)


def delete_projects_with_ids(project_id_list):
    for pid in project_id_list:
        impl.impl_delete_project(pid)
    return

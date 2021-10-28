import random

import tests.apps.core.projects.testutils as tu_projects
import tests.apps.core.users.testutils as tu_users
import apps.core.users.implementation as impl_users
import apps.core.projects.models as models


def test_get_subproject(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    secondary_user = tu_users.seed_random_user(admin=False, disabled=False)
    third_user = tu_users.seed_random_user(admin=False, disabled=False)
    p1 = tu_projects.seed_random_project(current_user.id,
                                         participants={
                                             secondary_user.id: models.AccessLevel.EDITOR,
                                             third_user.id: models.AccessLevel.EDITOR
                                         })
    p2 = tu_projects.seed_random_project(secondary_user.id,
                                         participants={
                                             current_user.id: models.AccessLevel.EDITOR,
                                             third_user.id: models.AccessLevel.EDITOR
                                         })
    p3 = tu_projects.seed_random_project(secondary_user.id,
                                         participants={
                                             third_user.id: models.AccessLevel.EDITOR
                                         })
    subprojects = [tu_projects.seed_random_subproject(current_user.id, p1.id),
                   tu_projects.seed_random_subproject(current_user.id, p2.id),
                   tu_projects.seed_random_subproject(secondary_user.id, p1.id),
                   tu_projects.seed_random_subproject(secondary_user.id, p2.id),
                   tu_projects.seed_random_subproject(secondary_user.id, p2.id),
                   tu_projects.seed_random_subproject(secondary_user.id, p3.id),
                   tu_projects.seed_random_subproject(third_user.id, p1.id),
                   tu_projects.seed_random_subproject(third_user.id, p2.id)]
    # Act
    res1 = client.get(f'/api/core/projects/{p1.id}/subprojects/', headers=std_headers)
    res2 = client.get(f'/api/core/projects/{p2.id}/subprojects/', headers=std_headers)
    res3 = client.get(f'/api/core/projects/{p3.id}/subprojects/', headers=std_headers)
    # Assert
    assert res1.status_code == 200
    assert len(res1.json()) == 3
    assert res2.status_code == 200
    assert len(res2.json()) == 4
    assert res3.status_code == 403
    # Cleanup
    tu_projects.delete_subprojects(subprojects)
    tu_projects.delete_projects([p1, p2, p3])
    tu_users.delete_users([secondary_user, third_user])


def test_create_subproject(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id)
    random_native_project_id = random.randint(0, 99999)
    app_sid = "MOD.EFM"
    # Act
    res = client.post(f'/api/core/projects/{p.id}/subprojects/',
                      headers=std_headers,
                      json={
                          "application_sid": app_sid,
                          "native_project_id": random_native_project_id
                      })
    res_sp = models.SubProject(**res.json())
    # Assert
    assert res.status_code == 200
    assert res_sp.project_id == p.id
    assert res_sp.application_sid == app_sid
    assert res_sp.owner_id == current_user.id
    assert res_sp.native_project_id == random_native_project_id
    # Cleanup
    tu_projects.delete_subprojects([res_sp])
    tu_projects.delete_projects([p])


def test_delete_subproject(client, std_headers, std_user):
    # Setup
    current_user = impl_users.impl_get_user_with_username(std_user.username)
    p = tu_projects.seed_random_project(current_user.id)
    sp = tu_projects.seed_random_subproject(current_user.id, p.id)
    # Act
    res1 = client.get(f'/api/core/projects/{p.id}/subprojects/{sp.id}', headers=std_headers)
    res2 = client.delete(f'/api/core/projects/{p.id}/subprojects/{sp.id}', headers=std_headers)
    res3 = client.get(f'/api/core/projects/{p.id}/subprojects/{sp.id}', headers=std_headers)

    # Assert
    assert res1.status_code == 200
    assert res2.status_code == 200
    assert res3.status_code == 404

    # Cleanup
    tu_projects.delete_projects([p])


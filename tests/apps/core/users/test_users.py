import pytest

import sedbackend.apps.core.users.implementation as users_impl
import sedbackend.apps.core.authentication.implementation as auth_impl
import sedbackend.apps.core.authentication.exceptions as auth_exc
import tests.testutils as tu
import tests.apps.core.users.testutils as tu_users
import pandas as pd


def test_create_user(client, admin_headers):
    # Act
    res = client.post("/api/core/users",
                      headers=admin_headers,
                      json={
                          "username": tu.random_str(3, 40),
                          "email": tu.random_str(3, 40) + "@gmail.com",
                          "full_name": tu.random_str(3, 40) + " " + tu.random_str(3,40),
                          "disabled": False,
                          "password": tu.random_str(8, 40),
                          "scopes": "user"
                      })
    # Assert
    assert res.status_code == 200

    # Clean
    users_impl.impl_delete_user_from_db(res.json()["id"])


def test_create_users_bulk_as_admin(client, admin_headers):
    # Setup
    test_file = 'tests/test_assets/core/users/bulk_user_sheet.xlsx'
    df_users = pd.read_excel(test_file)

    # Act
    files = {'file': ('bulk_user_sheet.xlsx', open(test_file, 'rb'))}
    res = client.post("/api/core/users/bulk", files=files, headers=admin_headers)

    # Assert
    assert res.status_code == 200
    for index, row in df_users.iterrows():
        assert users_impl.impl_get_user_with_username(row['username']).username == row['username']
        assert users_impl.impl_get_user_with_username(row['username']).disabled is None

    # Clean
    for index, row in df_users.iterrows():
        users_impl.impl_delete_user_from_db(users_impl.impl_get_user_with_username(row['username']).id)


def test_create_users_bulk(client, std_headers):
    # Setup
    test_file = 'tests/test_assets/core/users/bulk_user_sheet.xlsx'

    # Act
    files = {'file': ('bulk_user_sheet.xlsx', open(test_file, 'rb'))}
    res_1 = client.post("/api/core/users/bulk", files=files, headers=std_headers)
    res_2 = client.post("/api/core/users/bulk", files=files)

    # Assert
    assert res_1.status_code == 403
    assert res_2.status_code == 401


def test_delete_user_as_admin(client, admin_headers):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    # Act
    res = client.delete(f"/api/core/users/{new_user.id}", headers=admin_headers)
    # Assert
    assert res.status_code == 200


def test_delete_user(client, std_headers):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    # Act
    res = client.delete(f"/api/core/users/{new_user.id}", headers=std_headers)
    # Assert
    assert res.status_code == 403
    # Cleanup
    users_impl.impl_delete_user_from_db(new_user.id)


def test_get_user_as_admin(client, admin_headers):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    # Act
    res = client.get(f"/api/core/users/{new_user.id}", headers=admin_headers)
    # Assert
    assert res.status_code == 200
    assert res.json()["username"] == user.username
    assert res.json()["email"] == user.email
    assert res.json()["full_name"] == user.full_name
    assert res.json()["disabled"] == user.disabled
    # Clean
    users_impl.impl_delete_user_from_db(new_user.id)


def test_get_user_me_as_admin(client, admin_headers, admin_user):
    # Act
    res = client.get("/api/core/users/me", headers=admin_headers)
    # Assert
    assert res.status_code == 200
    assert res.json()["username"] == admin_user.username


def test_get_user_me(client, std_headers, std_user):
    # Act
    res = client.get("/api/core/users/me", headers=std_headers)
    # Assert
    assert res.status_code == 200
    assert res.json()["username"] == std_user.username


def test_get_users_unauthenticated(client):
    # Act
    res = client.get("/api/core/users")
    # Assert
    assert res.status_code == 401


def test_get_users(client, std_headers):
    # Setup
    users = [tu_users.seed_random_user(), tu_users.seed_random_user(), tu_users.seed_random_user()]

    # Act
    res = client.get("/api/core/users?segment_length=100&index=0&order_by=id&order_direction=desc", headers=std_headers)

    # Assert
    assert res.status_code == 200
    assert len(res.json()) > 0
    ids = []
    for u in res.json():
        ids.append(u["id"])
    for u in users:
        assert u.id in ids

    # Clean
    tu_users.delete_users(users)


def test_get_users_forbidden(client, std_headers):
    # Act
    res_1 = client.get(f'/api/core/users?segment_length=100&index=0&order_by=username&order_direction=desc', headers=std_headers)
    res_2 = client.get(f'/api/core/users?segment_length=100&index=0&order_by=password&order_direction=desc', headers=std_headers)
    res_3 = client.get(f'/api/core/users?segment_length=100&index=0&order_by=password&order_direction=blah', headers=std_headers)
    res_4 = client.get(f'/api/core/users?segment_length=100&index=0&order_by=username&order_direction=blah', headers=std_headers)

    # Assert
    assert res_1.status_code == 200
    assert res_2.status_code == 400
    assert res_3.status_code == 400
    assert res_4.status_code == 400


def test_search_users(client, std_headers):
    # Setup
    prefix_1 = 'search_test_' + tu.random_str(3, 3)
    prefix_2 = prefix_1 + '2' + tu.random_str(3, 3)
    prefix_3 = prefix_2 + '3' + tu.random_str(3, 3)
    u1 = tu_users.seed_random_user(name_prefix=prefix_1)
    u2 = tu_users.seed_random_user(name_prefix=prefix_2)
    u3 = tu_users.seed_random_user(name_prefix=prefix_3)

    # Act
    res_1 = client.get(f'/api/core/users/search?username={prefix_1}&order_by=username&order_direction=desc', headers=std_headers)
    res_2 = client.get(f'/api/core/users/search?username={prefix_2}', headers=std_headers)
    res_3 = client.get(f'/api/core/users/search?username={prefix_3}&order_by=id&order_direction=asc', headers=std_headers)

    # Assert
    assert res_1.status_code == 200 and res_2.status_code == 200 and res_3.status_code == 200
    assert len(res_1.json()) == 3
    assert len(res_2.json()) == 2
    assert len(res_3.json()) == 1

    # Clean
    tu_users.delete_users([u1, u2, u3])


def test_search_users_unauthenticated(client):
    # Setup
    prefix = tu.random_str(8, 8)
    user = tu_users.seed_random_user(name_prefix=prefix)

    # Act
    res = client.get(f'/api/core/users/search?username={prefix}')

    # Assert
    assert res.status_code == 401

    # Clean
    tu_users.delete_users([user])


def test_search_users_forbidden(client, std_headers):
    # Setup
    prefix = tu.random_str(8, 8)
    user = tu_users.seed_random_user(name_prefix=prefix)

    # Act
    res_1 = client.get(f'/api/core/users/search?username={prefix}&order_by=password', headers=std_headers)
    res_2 = client.get(f'/api/core/users/search?username={prefix}&order_direction=blah', headers=std_headers)

    # Assert
    assert res_1.status_code == 400     # Should be forbidden
    assert res_2.status_code == 400     # Should be forbidden

    # Clean
    tu_users.delete_users([user])


def test_post_user_unauthenticated(client):
    # Act
    res = client.post("/api/core/users",
                      json={
                          "username": tu.random_str(3, 40),
                          "email": tu.random_str(3, 40) + "@gmail.com",
                          "full_name": tu.random_str(3, 40) + " " + tu.random_str(3, 40),
                          "disabled": False,
                          "password": tu.random_str(8, 40),
                          "scopes": "user"
                      })
    # Assert
    assert res.status_code == 401


def test_get_me_unauthenticated(client):
    # Act
    res = client.get("/api/core/users/me")
    # Assert
    assert res.status_code == 401


def test_get_user_unauthenticated(client):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)

    # Act
    res = client.get(f"/api/core/users/{new_user.id}")

    # Assert
    assert res.status_code == 401

    # Cleanup
    users_impl.impl_delete_user_from_db(new_user.id)


def test_delete_user_unauthenticated(client):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)

    # Act
    res = client.delete(f"/api/core/users/{new_user.id}")
    user_exists = True
    user_check = users_impl.impl_get_user_with_id(new_user.id)

    if user_check is None:
        user_exists = False

    # Assert
    assert res.status_code == 401
    assert user_exists is True

    # Cleanup
    users_impl.impl_delete_user_from_db(new_user.id)


def test_update_details(client, std_headers, std_user):
    # Setup
    user = users_impl.impl_get_user_with_username(std_user.username)
    random_name = f'{tu.random_str(5, 20)} {tu.random_str(5, 20)}'
    random_email = f'{tu.random_str(5, 20)}@{tu.random_str(5, 20)}'

    # Act
    res = client.put(f'/api/core/users/{user.id}/details',
                     json={'full_name': random_name, 'email': random_email}, headers=std_headers)

    me = users_impl.impl_get_users_me(user)

    # Assert
    assert res.status_code == 200
    assert me.id == user.id
    assert me.full_name == random_name
    assert me.email == random_email


def test_update_details_of_other_user(client, std_headers, std_user):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    random_name = f'{tu.random_str(5, 20)} {tu.random_str(5, 20)}'
    random_email = f'{tu.random_str(5, 20)}@{tu.random_str(5, 20)}'

    # Act
    res = client.put(f'/api/core/users/{new_user.id}/details',
                     json={'full_name': random_name, 'email': random_email}, headers=std_headers)

    new_user_refreshed = users_impl.impl_get_user_with_id(new_user.id)

    # Assert
    assert res.status_code == 403
    assert new_user_refreshed.id == new_user.id
    assert new_user_refreshed.full_name != random_name
    assert new_user_refreshed.email != random_email


def test_update_password(client, std_headers, std_user):
    # Setup
    user = users_impl.impl_get_user_with_username(std_user.username)
    random_pwd = tu.random_str(8, 20)

    # Act
    res = client.put(f'/api/core/users/{user.id}/password',
                     json={'current_password': std_user.password, 'new_password': random_pwd}, headers=std_headers)

    # Assert
    assert res.status_code == 200
    with pytest.raises(auth_exc.InvalidCredentialsException):
        auth_impl.login(std_user.username, std_user.password)
    auth_impl.login(std_user.username, random_pwd)

    # Cleanup
    client.put(f'/api/core/users/{user.id}/password',
               json={'current_password': random_pwd, 'new_password': std_user.password}, headers=std_headers)


def test_update_other_user_password(client, std_headers, std_user):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    random_pwd = tu.random_str(8, 10)

    # Act
    res = client.put(f'/api/core/users/{new_user.id}/password',
                     json={'current_password': None, 'new_password': random_pwd}, headers=std_headers)

    # Assert
    assert res.status_code == 403
    with pytest.raises(auth_exc.InvalidCredentialsException):
        auth_impl.login(new_user.username, random_pwd)

    # Cleanup
    users_impl.impl_delete_user_from_db(new_user.id)


def test_update_other_user_password_as_admin(client, admin_headers, admin_user):
    # Setup
    user = tu_users.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    random_pwd = tu.random_str(8, 10)

    # Act
    res = client.put(f'/api/core/users/{new_user.id}/password',
                     json={'current_password': None, 'new_password': random_pwd}, headers=admin_headers)

    # Assert
    assert res.status_code == 200
    auth_impl.login(new_user.username, random_pwd)

    # Cleanup
    users_impl.impl_delete_user_from_db(new_user.id)


def test_update_other_admin_password_as_admin(client, admin_headers, admin_user):
    # Setup
    admin = tu_users.random_user_post(admin=True, disabled=False)
    new_admin = users_impl.impl_post_user(admin)
    random_pwd = tu.random_str(8, 10)

    # Act
    res = client.put(f'/api/core/users/{new_admin.id}/password',
                     json={'current_password': None, 'new_password': random_pwd}, headers=admin_headers)

    # Assert
    assert res.status_code == 403
    with pytest.raises(auth_exc.InvalidCredentialsException):
        auth_impl.login(new_admin.username, random_pwd)
    auth_impl.login(new_admin.username, admin.password)

    # Cleanup
    users_impl.impl_delete_user_from_db(new_admin.id)


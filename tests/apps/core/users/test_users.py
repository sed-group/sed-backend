import sedbackend.apps.core.users.implementation as users_impl
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
    df_users = pd.read_excel(test_file)

    # Act
    files = {'file': ('bulk_user_sheet.xlsx', open(test_file, 'rb'))}
    res_1 = client.post("/api/core/users/bulk", files=files, headers=std_headers)
    res_2 = client.post("/api/core/users/bulk", files=files)

    # Assert
    assert res_1.status_code == 401
    assert res_2.status_code == 403


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


def test_get_user_me(client, std_headers, std_user, request):
    # Act
    res = client.get("/api/core/users/me", headers=std_headers)
    # Assert
    assert res.status_code == 200
    assert res.json()["username"] == std_user.username


def test_get_users_unauthenticated(client):
    # Act
    res = client.get("/api/core/users/users")
    # Assert
    assert res.status_code == 401


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

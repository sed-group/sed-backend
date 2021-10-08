import apps.core.users.implementation as users_impl
import tests.testutils as testutils


def test_create_user(client, admin_headers):
    # Act
    res = client.post("/api/core/users/",
                      headers=admin_headers,
                      json={
                          "username": testutils.random_str(3, 40),
                          "email": testutils.random_str(3, 40) + "@gmail.com",
                          "full_name": testutils.random_str(3, 40) + " " + testutils.random_str(3,40),
                          "disabled": False,
                          "password": testutils.random_str(8, 40),
                          "scopes": "user"
                      })
    # Assert
    assert res.status_code == 200

    # Clean
    users_impl.impl_delete_user_from_db(res.json()["id"])


def test_delete_user(client, admin_headers):
    # Setup
    user = testutils.random_user_post(admin=False, disabled=False)
    new_user = users_impl.impl_post_user(user)
    # Act
    res = client.delete(f"/api/core/users/{new_user.id}", headers=admin_headers)
    # Assert
    assert res.status_code == 200


def test_get_user_as_admin(client, admin_headers):
    # Setup
    user = testutils.random_user_post(admin=False, disabled=False)
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

from typing import List

import sedbackend.apps.core.users.models as models
import sedbackend.apps.core.users.implementation as impl
import tests.testutils as tu


def random_user_post(admin=False, disabled=False) -> models.UserPost:
    random_name = 'test_user_' + tu.random_str(5, 15)
    random_email = random_name + "@sed-mock-email.com"
    random_password = tu.random_str(5, 20)

    user = models.UserPost(
        username=random_name,
        email=random_email,
        disabled=disabled,
        password=random_password,
    )

    if admin is True:
        user.scopes = 'admin'
    else:
        user.scopes = 'user'

    return user


def seed_random_user(admin=False, disabled=False) -> models.User:
    user_post = random_user_post(admin=admin, disabled=disabled)
    user = impl.impl_post_user(user_post)
    return user


def delete_users(users: List[models.User]):
    for u in users:
        impl.impl_delete_user_from_db(u.id)

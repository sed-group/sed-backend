import random

import apps.core.users.models as models_users


def random_str(min_length, max_length):
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    numbers = "0123456789"
    return ''.join(random.choice(alphabet + numbers) for _ in range(random.randint(min_length, max_length)))


def random_user_post(admin=False, disabled=False) -> models_users.UserPost:
    random_name = 'test_user_' + random_str(5, 15)
    random_email = random_name + "@sed-mock-email.com"
    random_password = random_str(5, 20)

    user = models_users.UserPost(
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

import apps.core.users.models as models
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

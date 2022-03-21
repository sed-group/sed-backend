class UserNotFoundException(Exception):
    """
    Thrown when a user can't be found in the database
    """
    pass


class UserNotUniqueException(Exception):
    """
    Thrown when a user with a non-unique username is created (which is restricted in the database)
    """
    pass


class UserDisabledException(Exception):
    """
    Thrown when a disabled user attempts to do anything
    """
    pass

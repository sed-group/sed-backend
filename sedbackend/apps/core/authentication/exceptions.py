class InvalidCredentialsException(Exception):
    """
    Thrown when login credentials are incorrect
    """
    pass


class UnauthorizedOperationException(Exception):
    """
    Thrown when a user attempts to do something that is not allowed
    """
    pass

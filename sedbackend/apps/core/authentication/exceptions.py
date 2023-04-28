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


class InvalidNonceException(Exception):
    """
    Thrown when a user attempts to resolve an invalid Nonce
    """
    pass


class FaultyNonceOperation(Exception):
    """
    Thrown when inserting or resolving a nonce fails without a known cause
    """
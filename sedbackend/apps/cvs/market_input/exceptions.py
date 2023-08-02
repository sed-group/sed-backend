class ExternalFactorNotFoundException(Exception):
    pass


class ExternalFactorAlreadyExistException(Exception):
    pass


class WrongTimeUnitException(Exception):
    def __init__(self, time_unit: str = None) -> None:
        self.time_unit = time_unit


class ExternalFactorFailedDeletionException(Exception):
    pass


class ExternalFactorFormulasNotFoundException(Exception):
    pass

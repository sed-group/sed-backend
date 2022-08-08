class FormulasNotFoundException(Exception):
    pass

class WrongTimeUnitException(Exception):
    def __init__(self, time_unit: str = None ) -> None:
        self.time_unit = time_unit

class VCSNotFoundException(Exception):
    pass

class FormulasFailedUpdateException(Exception):
    pass

class FormulasFailedDeletionException(Exception):
    pass
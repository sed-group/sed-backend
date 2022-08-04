class MarketInputNotFoundException(Exception):
    pass


class MarketInputAlreadyExistException(Exception):
    pass

class WrongTimeUnitException(Exception):
    def __init__(self, time_unit: str = None ) -> None:
        self.time_unit = time_unit

class MarketInputFailedDeletionException(Exception):
    pass

class MarketInputFormulasNotFoundException(Exception):
    pass
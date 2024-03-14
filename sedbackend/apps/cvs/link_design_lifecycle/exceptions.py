class FormulasNotFoundException(Exception):
    pass


class VCSNotFoundException(Exception):
    pass


class FormulasFailedUpdateException(Exception):
    pass


class FormulasFailedDeletionException(Exception):
    pass


class TooManyFormulasUpdatedException(Exception):
    pass


class CouldNotAddValueDriverToProjectException(Exception):
    pass

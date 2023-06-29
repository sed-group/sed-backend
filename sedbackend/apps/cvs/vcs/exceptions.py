# ======================================================================================================================
# VCS
# ======================================================================================================================


class VCSNotFoundException(Exception):
    pass


class VCSFailedToUpdateException(Exception):
    pass


class VCSFailedDeletionException(Exception):
    pass


class VCSYearFromGreaterThanYearToException(Exception):
    pass


class GenericDatabaseException(Exception):
    def __init__(self, msg: str = None):
        self.msg = msg


# ======================================================================================================================
# VCS Value dimensions
# ======================================================================================================================


class ValueDimensionNotFoundException(Exception):
    pass


class ValueDimensionFailedDeletionException(Exception):
    pass


# ======================================================================================================================
# VCS Value driver
# ======================================================================================================================


class ValueDriverNotFoundException(Exception):
    def __init__(self, value_driver_id: int = None):
        self.value_driver_id = value_driver_id


class ValueDriverFailedToUpdateException(Exception):
    pass


class ValueDriverFailedDeletionException(Exception):
    pass


class ValueDriverFailedToCreateException(Exception):
    pass


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================


class ISOProcessNotFoundException(Exception):
    pass


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================


class SubprocessNotFoundException(Exception):
    def __init__(self, subprocess_id: int = None):
        self.subprocess_id = subprocess_id


class SubprocessFailedToUpdateException(Exception):
    def __init__(self, subprocess_id: int = None):
        self.subprocess_id = subprocess_id


class SubprocessFailedDeletionException(Exception):
    def __init__(self, subprocess_id: int = None):
        self.subprocess_id = subprocess_id


class SubprocessFailedCreationException(Exception):
    pass


# ======================================================================================================================
# VCS Table
# ======================================================================================================================


class VCSTableRowNotFoundException(Exception):
    pass


class VCSTableRowFailedToUpdateException(Exception):
    pass


class VCSTableRowFailedDeletionException(Exception):
    def __init__(self, table_row_id: int = None):
        self.table_row_id = table_row_id


class VCSTableProcessAmbiguity(Exception):
    def __init__(self, table_row_id: int = None):
        self.table_row_id = table_row_id


class VCSRowNotCorrectException(Exception):
    pass


class VCSandVCSRowIDMismatchException(Exception):
    pass


# ======================================================================================================================
# VCS Stakeholder needs
# ======================================================================================================================

class VCSStakeholderNeedNotFound(Exception):
    pass


class VCSStakeholderNeedFailedDeletionException(Exception):
    pass


class VCSStakeholderNeedFailedCreationException(Exception):
    pass


class VCSStakeholderNeedFailedToUpdateException(Exception):
    pass

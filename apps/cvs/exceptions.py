# ======================================================================================================================
# CVS projects
# ======================================================================================================================

class CVSProjectNotFoundException(Exception):
    pass


class CVSProjectFailedToUpdateException(Exception):
    pass


class CVSProjectFailedDeletionException(Exception):
    pass


# ======================================================================================================================
# VCS (Value Creation Strategy)
# ======================================================================================================================

class VCSNotFoundException(Exception):
    pass


class VCSFailedToUpdateException(Exception):
    pass


class VCSFailedDeletionException(Exception):
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


# ======================================================================================================================
# VCS ISO Processes
# ======================================================================================================================

class ISOProcessNotFoundException(Exception):
    pass


# ======================================================================================================================
# VCS Subprocesses
# ======================================================================================================================

class SubprocessNotFoundException(Exception):
    pass


class SubprocessFailedToUpdateException(Exception):
    pass


class SubprocessFailedDeletionException(Exception):
    pass


# ======================================================================================================================
# VCS Table
# ======================================================================================================================

class VCSTableRowNotFoundException(Exception):
    pass


class VCSTableRowFailedToUpdateException(Exception):
    pass


class VCSTableRowFailedDeletionException(Exception):
    def __init__(self, table_row_id):
        self.table_row_id = table_row_id


class VCSTableProcessAmbiguity(Exception):
    def __init__(self, table_row_id):
        self.table_row_id = table_row_id

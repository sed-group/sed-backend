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
    pass


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

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
# VCS - Value Creation Strategy
# ======================================================================================================================

class VCSNotFoundException(Exception):
    pass


class VCSFailedToUpdateException(Exception):
    pass


class VCSFailedDeletionException(Exception):
    pass


# ======================================================================================================================
# VCS - Value Creation Strategy
# ======================================================================================================================

class ValueDriverNotFoundException(Exception):
    pass


class ValueDriverFailedToUpdateException(Exception):
    pass


class ValueDriverFailedDeletionException(Exception):
    pass

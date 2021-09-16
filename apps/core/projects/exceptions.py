class ProjectNotFoundException(Exception):
    pass


class ProjectNotDeletedException(Exception):
    pass


class ParticipantChangeException(Exception):
    pass


class ProjectChangeException(Exception):
    pass


class SubProjectNotFoundException(Exception):
    pass


class ProjectInsertFailureException(Exception):
    pass


class SubProjectNotDeletedException(Exception):
    pass


class NoParticipantsException(Exception):
    pass


class SubProjectDuplicateException(Exception):
    pass


class ParticipantInconsistencyException(Exception):
    pass

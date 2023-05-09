class NodeNotFoundException(Exception):
    pass


class NodeIdDontMatchVCSIdException(Exception):
    pass


class NodeFailedDeletionException(Exception):
    def __init__(self, node_id: int = None):
        self.node_id = node_id


class InvalidNodeType(Exception):
    pass


class NodeFailedToUpdateException(Exception):
    pass


class InvalidFileTypeException(Exception):
    pass
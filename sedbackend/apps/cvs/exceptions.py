

# ======================================================================================================================
# BPMN Table
# ======================================================================================================================

class NodeNotFoundException(Exception):
    pass


class NodeIdDontMatchVCSIdException(Exception):
    pass


class NodeFailedDeletionException(Exception):
    def __init__(self, node_id: int = None):
        self.node_id = node_id


class NodeFailedToUpdateException(Exception):
    pass


class EdgeNotFoundException(Exception):
    pass


class EdgeFailedDeletionException(Exception):
    def __init__(self, edge_id: int = None):
        self.edge_id = edge_id


class EdgeFailedToUpdateException(Exception):
    pass


# ======================================================================================================================
# Design
# ======================================================================================================================


class DesignNotFoundException(Exception):
    pass


# ======================================================================================================================
# Market input
# ======================================================================================================================

class MarketInputNotFoundException(Exception):
    pass


class MarketInputAlreadyExistException(Exception):
    pass

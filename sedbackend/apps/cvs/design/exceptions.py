
# ======================================================================================================================
# Design
# ======================================================================================================================


class DesignNotFoundException(Exception):
    pass


class DesignGroupNotFoundException(Exception):
    pass

class DesignGroupInsertException(Exception):
    pass

class DesignInsertException(Exception):
    pass

# ======================================================================================================================
# Quantified Objectives
# ======================================================================================================================


class QuantifiedObjectiveNotFoundException(Exception):
    pass


class QuantifiedObjectivesNotDeleted(Exception):
    pass


class QuantifiedObjectiveValueNotFoundException(Exception):
    pass


class QuantifiedObjectiveValueNotDeleted(Exception):
    pass

class QuantifiedObjectiveNotInFormulas(Exception):
    pass
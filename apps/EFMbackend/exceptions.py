class EfmElementNotFoundException(Exception):
    """
    Thrown when a EFM element (FR, DS, ...) can't be found
    """
    pass

class EfmElementNotInTreeException(Exception):
    """
    Thrown when an element is to be moved out of the project,
    or to be related to an object in another project,
    or other unwanted inter-project relations are coming up
    """
    pass

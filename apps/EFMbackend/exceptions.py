class EfmElementNotFoundException(Exception):
    """
    Thrown when a EFM element (FR, DS, ...) can't be found
    """
    def __init__(self, efm_type: str, efm_id: int):
        self.efm_type = efm_type
        self.efm_id = efm_id
        self.message = f"Could not find {efm_type} with ID {efm_id}."
        super().__init__(self.message)

    def __str__(self):
        return self.message



class EfmElementNotInTreeException(Exception):
    """
    Thrown when an element is to be moved out of the project,
    or to be related to an object in another project,
    or other unwanted inter-project relations are coming up
    """
    
    def __init__(self, efm_type: str, efm_id: int, tree_id: int):
        self.efm_type = efm_type
        self.efm_id = efm_id
        self.message = f"EFM element with ID {efm_id} with ID {efm_id} is not in tree ID {tree_id}."
        super().__init__(self.message)

    def __str__(self):
        return self.message

class EfmDatabaseException(Exception):
    '''
    Thrown when the SQL operation fails
    '''
    pass
from enum import Enum

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, ForwardRef

## importing from EF-M submodules
from apps.EFMbackend.parameters.schemas import DesignParameter

class TreeNew(BaseModel):
    '''
    base class for new trees
    only contains information that is collected during setup of tree
    '''
    name: str
    description: Optional[str]

class TreeInfo(TreeNew):
    '''
    tree class only containing header info
    '''
    id: int
    top_level_ds_id: Optional[int]

class IWnew(BaseModel):
    tree_id: Optional[int]
    from_ds_id: int
    to_ds_id: int
    iw_type: Optional[str] = 'spatial'
    description: Optional[str]

class InteractsWith(IWnew):
    id: int
    
## CONCEPTS
class ConceptEdit(BaseModel):
    '''
    externally editable information of a concept
    '''
    name: str
    tree_id: Optional[int]

class ConceptNew(ConceptEdit):
    ''' 
    used in create all instances to create new concept (with new DNA)
    '''
    dna: str

class Concept(ConceptNew):
    """
    one instance of a concept of a tree
    """
    id: Optional[int]
    
    def dnaList(self):
        return self.dna.split(',')


## DESIGNSOLUTIONS
class DSnew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = None
    isb_id: Optional[int] = None
    tree_id: Optional[int] = None
    is_top_level_ds: Optional[bool] = False

class DesignSolution(DSnew):
    """
    DS element for EF-M modelling; contains all basic information
    """
    id: Optional[int] = None
            
## FUNCTIONAL REQUIREMENTS
class FRnew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = ""
    tree_id: Optional[int]
    rf_id: int

class FunctionalRequirement(FRnew):
    """
    FR element for EF-M modelling; contains all basic information
    """
    id: Optional[int] = None

class ConstraintNew(BaseModel): 
    name: str
    description: Optional[str] = ""
    tree_id: Optional[int]
    icb_id: int

class Constraint(ConstraintNew):
    '''
        symbolic constraint element for use in UI
    '''
    id: int

## TREE DATA
class TreeData(TreeInfo):
    ''' 
    data dump of an entire tree
    '''
    ds: List[DesignSolution] = []
    fr: List[FunctionalRequirement] = []
    iw: List[InteractsWith] = []
    dp: List[DesignParameter] = []
    c: List[Constraint] = []






 
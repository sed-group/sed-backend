from datetime import datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, ForwardRef

## importing from EF-M submodules
from apps.EFMbackend.parameters.schemas import DesignParameter

FunctionalRequirementTemp = ForwardRef('FunctionalRequirement')
DesignSolutionTemp = ForwardRef('DesignSolution')
ConceptTemp = ForwardRef('Concept')

class TreeNew(BaseModel):
    '''
    base class for new trees
    only contains information that is collected during setup of tree
    '''
    name: str
    description: Optional[str]

class TreeInfo(TreeNew):
    '''
    tree class only containing header info, 
    no actual tree
    '''
    id: int
    top_level_ds_id: Optional[int]
    subproject_id: Optional[int]

class Tree(TreeInfo):
    """
    tree class including all fields
    """
    concepts: List[ConceptTemp] = []
    #fr: List[FunctionalRequirementTemp] = []
    #ds: List[DesignSolutionTemp] = []   
    ### circular link to DS not working because of bug see https://github.com/samuelcolvin/pydantic/issues/2279
    top_level_ds: Optional[DesignSolutionTemp] = None

    class Config:
        orm_mode = True

# ## INTERACTS WITH
# class iwType(str, Enum):
#     SP = 'spatial'
#     EN = 'energy'
#     MA = 'material flow'
#     IN = 'information'

class IWnew(BaseModel):
    tree_id: Optional[int]
    from_ds_id: int
    to_ds_id: int
    iw_type: Optional[str] = 'spatial'
    description: Optional[str]

class InteractsWith(IWnew):
    id: int
    
    class Config:
        orm_mode = True
    
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

class Concept(ConceptEdit):
    """
    one instance of a tree of a tree
    """
    id: Optional[int]
    dna: str
    #tree: Tree
    
    class Config:
        orm_mode = True
    
    def dnaList(self):
        return self.dna.split(',')

class ConceptTree(ConceptEdit):
    '''
    contains a tree structure in topLvlDS like a project tree
    however it is pruned to only the DS included in the concept,
    i.e. FR:DS 1:1
    '''
    top_level_ds: Optional[DesignSolutionTemp]

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
    #isb: Optional[FunctionalRequirementTemp]
    requires_functions: List[FunctionalRequirementTemp] = []
    #tree: Tree

    interacts_with: List[InteractsWith] = []
    design_parameters: List[DesignParameter] = []
        
    class Config:
        orm_mode = True

class DSinfo(DSnew):
    '''
    a DS class without the list of requires_function FR, but FRids instead
    as such it doesn't carry the entire tree
    same for iw and DP
    '''
    id: int
    requires_functions_id: Optional[List[int]] = []
    interacts_with_id: Optional[List[int]] = []
    design_parameter_id: Optional[List[int]] = []

    is_top_level_ds: Optional[bool] = False

    def update(self, originalDS: DesignSolution):

        for fr in originalDS.requires_functions:
            self.requires_functions_id.append(fr.id)

        for iw in originalDS.interacts_with:
            self.interacts_with_id.append(iw.id)

        for dp in originalDS.design_parameters:
            self.design_parameter_id.append(dp.id)

## FUNCTIONAL REQUIREMENTS
class FRNew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = None
    tree_id: Optional[int] = None
    rf_id: int

class FunctionalRequirement(FRNew):
    """
    FR element for EF-M modelling; contains all basic information
    """
    id: Optional[int] = None
    #tree: Tree
    #rf: DesignSolution
    is_solved_by: List[DesignSolution] = []
        
    class Config:
        orm_mode = True

class FRinfo(FRNew):
    '''
    a DS class without the list of requires_function FR, but FRids instead
    as such it doesn't carry the entire tree
    same for iw and DP
    '''
    id: int
    is_solved_by_id: Optional[List[int]] = []

    def update(self, originalFR: FunctionalRequirement):

        for ds in originalFR.is_solved_by:
            self.is_solved_by_id.append(ds.id)


## TREE DATA
class TreeData(TreeInfo):
    ''' 
    data dump of an entire tree
    '''
    ds: List[DSinfo] = []
    fr: List[FRinfo] = []
    iw: List[InteractsWith] = []
    dp: List[DesignParameter] = []
    
    class Config:
        orm_mode = True

# to be able to use "FunctionalRequirement" (etc) in DS, Tree before defining it, we need to update the forward references:
DesignSolution.update_forward_refs()
Tree.update_forward_refs()
ConceptTree.update_forward_refs()



 
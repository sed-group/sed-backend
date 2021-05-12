from datetime import datetime

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
    description: str

class Tree(TreeNew):
    """
    tree class including all fields
    """
    id: Optional[int]
    concepts: List[ConceptTemp] = []
    #fr: List[FunctionalRequirementTemp] = []
    #ds: List[DesignSolutionTemp] = []   
    ### circular link to DS not working because of bug see https://github.com/samuelcolvin/pydantic/issues/2279
    topLvlDS: Optional[DesignSolutionTemp] = None
    topLvlDSid: Optional[int] = None 

    class Config:
        orm_mode = True

## INTERACTS WITH
class IWnew(BaseModel):
    treeID: int
    fromDsID: int
    toDsID: int
    iwType: str

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
    treeID: Optional[int]

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
    topLvlDS: Optional[DesignSolutionTemp]

## DESIGNSOLUTIONS
class DSnew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = None
    treeID: int
    isbID: Optional[int] = None
    is_top_level_DS: Optional[bool] = False

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

    is_top_level_DS: Optional[bool] = False

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
    treeID: int
    rfID: Optional[int]
    # one might want to discuss why we have _both_ rfID (parentDS) _AND_ treeID, where the parentDS already contains the treeID (and we check for that match, don't worry!). the answer is that in the future we might want to be able to create FR (or even DS) without a parent, "floating" so to speak.

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
class TreeData(TreeNew):
    ''' 
    data dump of an entire tree
    '''
    id: int
    topLvlDSid: int

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



 
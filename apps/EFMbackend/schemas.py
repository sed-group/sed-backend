from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, ForwardRef

FunctionalRequirementTemp = ForwardRef('FunctionalRequirement')
DesignSolutionTemp = ForwardRef('DesignSolution')
ConceptTemp = ForwardRef('Concept')

class ProjectNew(BaseModel):
    '''
    base class for new projects
    only contains information that is collected during setup of project
    '''
    name: str
    description: str

class Project(ProjectNew):
    """
    project class including all fields
    """
    id: Optional[int]
    concepts: List[ConceptTemp] = []
    fr: List[FunctionalRequirementTemp] = []
    ds: List[DesignSolutionTemp] = []   
    ### circular link to DS not working because of bug see https://github.com/samuelcolvin/pydantic/issues/2279
    # topLvlDS: Optional[DesignSolutionTemp] = None
    topLvlDSid: Optional[int] = None 

    class Config:
        orm_mode = True


class Concept(BaseModel):
    """
    one instance of a tree of a project
    """
    id: Optional[int]
    name: str
    projectID: int
    #project: Project
    
    class Config:
        orm_mode = True

class DSnew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = None
    projectID: int
    isbID: Optional[int] = None

class DesignSolution(DSnew):
    """
    DS element for EF-M modelling; contains all basic information
    """
    id: Optional[int] = None
    #isb: Optional[FunctionalRequirementTemp]
    requires_functions: List[FunctionalRequirementTemp] = []
    #project: Project
    is_top_level_DS: Optional[bool] = False
        
    class Config:
        orm_mode = True

class DSinfo(DSnew):
    '''
    a DS class without the list of requires_function FR, but FRids instead
    as such it doesn't carry the entire tree
    '''
    id: int
    requires_functions_id: Optional[List[int]] = []
    is_top_level_DS: Optional[bool] = False

    # def __init__(self, originalDS: DesignSolution):
    #     self.name = originalDS.name
    #     self.description = originalDS.description
    #     self.projectID = originalDS.projectID
    #     self.isbID = originalDS.projectID
    #     self.id = originalDS.id
    #     self.is_top_level_DS = originalDS.is_top_level_DS

    #     for fr in originalDS.requires_functions:
    #         self.requires_functions_id.append(fr.id)

class FRNew(BaseModel):
    '''
    DS class for creation of new DS; contains only minimum viable info
    '''
    name: str
    description: Optional[str] = None
    projectID: int
    rfID: Optional[int]
    # one might want to discuss why we have _both_ rfID (parentDS) _AND_ projectID, where the parentDS already contains the projectID (and we check for that match, don't worry!). the answer is that in the future we might want to be able to create FR (or even DS) without a parent, "floating" so to speak.

class FunctionalRequirement(FRNew):
    """
    FR element for EF-M modelling; contains all basic information
    """
    id: Optional[int] = None
    #project: Project
    #rf: DesignSolution
    is_solved_by: List[DesignSolution] = []
        
    class Config:
        orm_mode = True
        
# to be able to use "FunctionalRequirement" (etc) in DS, Project before defining it, we need to update the forward references:
DesignSolution.update_forward_refs()
Project.update_forward_refs()


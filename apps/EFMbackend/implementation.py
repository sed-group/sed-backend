from sqlalchemy.orm import Session, lazyload, subqueryload
from fastapi import HTTPException, status


import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas
from apps.EFMbackend.exceptions import *

# from apps.core.db import get_connection
# from apps.EFMbackend.models import *
# from apps.EFMbackend.exceptions import *
# import apps.EFMbackend.storage as storage

#### PROJECTS
def get_project_list(db: Session, limit:int = 100, offset:int = 0):
    '''
    list of all project objects from DB
    '''
    return db.query(models.Project).offset(offset).limit(limit).all()

def create_project(db: Session, newProject = schemas.ProjectNew):
    '''
        creates one new project based on schemas.projectNew 
        creates a top-level DS and associates its ID to project.topLvlDSid
    '''
    # create project without DS:
    theProject = models.Project(**newProject.dict())
    db.add(theProject)
    db.commit()

    # create a top-levelDS:
    topDS = models.DesignSolution(name=newProject.name, description="Top-level DS", projectID = theProject.id, is_top_level_DS = True)
    db.add(topDS)
    db.commit()

    # setting the project topLvlDS
    theProject.topLvlDSid = topDS.id
    db.commit()

    return theProject

def get_project_details(db:Session, projectID: int):
    ''' 
        returns a project object with all details
    '''
    try:
        theProject = db.query(models.Project).filter(models.Project.id == projectID).first()
        if theProject:
            return theProject
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project with ID {} does not exist.".format(projectID)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project with ID {} does not exist.".format(projectID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="projectID needs to be an integer"
        )

def delete_project(db: Session, projectID: int):
    '''
        deletes project based on id 
    '''
    try:
        db.query(models.Project).filter(models.Project.id == projectID).delete()
        db.commit()
        return True
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project with ID {} does not exist.".format(projectID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="projectID needs to be an integer"
        )

### FR
def get_FR(db:Session, FRid: int):
    ''' 
        returns a FR object with all details
    '''
    try:
        theFR = db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == FRid).first()
        if theFR:
            return theFR
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FR with ID {} does not exist.".format(FRid)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FR with ID {} does not exist.".format(FRid)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="frID needs to be an integer"
        )

def create_FR(db: Session, parentID: int, newFR: schemas.DSnew):
    '''
        creates new FR based on schemas.FRnew (name, description) 
        associates it to DS with parentID via FR.rfID ("requires function")
    '''
    newFR.rfID = parentID

    # check for same project 
    try:
        theParent = db.query(models.DesignSolution).filter(models.DesignSolution.id == parentID).first()
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new FR; parent DS with ID {} cannot be found.".format(parentID)
        )
    
    if theParent.projectID != newFR.projectID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new FR; parent DS is in another project! parentProjectID: {}, FRprojectID: {}".format(theParent.projectID, newFR.projectID)
        )

    obj = models.FunctionalRequirement(**newFR.dict())
    db.add(obj)
    db.commit()
    return obj
    
def delete_FR(db: Session, FRid: int):
    '''
        deletes FR based on id 
    '''
    try:
        db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == FRid).delete()
        db.commit()
        return True
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FR with ID {} does not exist.".format(FRid)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="FRid needs to be an integer"
        )

def edit_FR(db: Session, FRid: int, FRdata: schemas.FRNew):
    '''
        overwrites the data in the FR identified with FRid with the data from FRdata
        can change parent (i.e. isb), name and description
        checks whether the new parent FR is in the same project
        cannot change project! (projectID)
    '''
    theFR = db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == FRid).first()
    theFR.name = FRdata.name
    theFR.description = FRdata.description

    # check if we need to change parent, too:
    if FRdata.rfID != theFR.rfID:
        theNewParent = db.query(models.DesignSolution).filter(models.DesignSolution.id == FRdata.rfID).first()

        # check if we are in the same project
        if theNewParent.project == theFR.project:
            theFR.rfID = theNewParent.id
        else:
            raise EfmElementNotInProjectException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit FR; new parent DS is in another project"
            )
    db.commit()
    return theFR
    
### DS
def get_DS(db:Session, DSid: int):
    ''' 
        returns a DS object with all details
    '''
    try:
        theDS = db.query(models.DesignSolution).options(subqueryload('requires_functions')).filter(models.DesignSolution.id == DSid).first()
        if theDS:
            return theDS
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DS with ID {} does not exist.".format(DSid)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DS with ID {} does not exist.".format(DSid)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DSid needs to be an integer"
        )

def create_DS(db: Session, parentID: int, newDS: schemas.DSnew):
    '''
        creates new DS based on schemas.DSnew (name, description) 
        associates it to 
    '''
    newDS.isbID = parentID

    # check if parent exists
    try:
        theParent = db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == parentID).first()
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new DS; parent FR with ID {} cannot be found.".format(parentID)
        )

    # check for project similarity
    if theParent.projectID != newDS.projectID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new DS; parent FR is in another project! (DS parent ID: {}, FR parent ID: {}".format(newDS.projectID, theParent.projectID)
        )
        
    obj = models.DesignSolution(**newDS.dict())
    db.add(obj)
    db.commit()
    return obj
    
def delete_DS(db: Session, DSid: int):
    '''
        deletes DS based on id 
    '''
    try:
        db.query(models.DesignSolution).filter(models.DesignSolution.id == DSid).delete()
        db.commit()
        return True 
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DS with ID {} does not exist.".format(DSid)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DSid needs to be an integer"
        )

def edit_DS(db: Session, DSid: int, DSdata: schemas.DSnew):
    '''
        overwrites the data in the DS identified with DSid with the data from DSnew
        can change parent (i.e. isb), name and description
        checks whether the new parent FR is in the same project
        cannot change project! (projectID)
    '''
    theDS = db.query(models.DesignSolution).filter(models.DesignSolution.id == DSid).first()
    theDS.name = DSdata.name
    theDS.description = DSdata.description

    # check if we need to change parent, too:
    if DSdata.isbID != theDS.isbID:
        try:
            theNewParent = db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == DSdata.isbID).first()
        except EfmElementNotFoundException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create new DS; parent FR cannot be found."
            )

        # check if we are in the same project
        if theNewParent.project == theDS.project:
            theDS.isbID = theNewParent.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit DS; new parent FR is in another project"
            )
    db.commit()
    return theDS
 

#  {
#     "name":"TestFR",
#     "description":"just a test?",
#     "projectID":2,
#     "rfID":2,
#     "id":1,
#     "project": {
#         "name": "foobar",
#         "description":"The Foo Barters",
#         "id":2,
#         "concepts":[],
#         "fr":[],
#         "ds":[],
#         "topLvlDSid":2
#         },
#     "is_solved_by":[
#         {"name":"ds child",
#         "description":"child test 1",
#         "projectID":2,
#         "isbID":1,
#         "id":4,
#         "requires_functions":[],
#         "project":{
#             "name":"foobar",
#             "description":"The Foo Barters",
#             "id":2,"concepts":[],
#             "fr":[],
#             "ds":[],
#             "topLvlDSid":2
#             },
#         "is_top_level_DS":false}
#     ]
# }
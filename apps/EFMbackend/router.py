from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from typing import List

# from .models import *
from apps.EFMbackend.database import SessionLocal
import apps.EFMbackend.implementation as implementation
import apps.EFMbackend.schemas as schemas

router = APIRouter()

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

## PROJECTS
@router.get("/projects/",
            response_model=List[schemas.Project],
            summary="Overview over all projects",  
            description="Produces a list of all projects",
            dependencies=[],
            # needs authentication to filter projects by user scope
            )
async def get_all_projects(db: Session = Depends(get_db)):
   return implementation.get_project_list(db)
   
@router.post("/projects/", 
            response_model=schemas.Project,
            summary="creating a new project",
            description="creates a new project including topLvlDS and returns the project object",
            )
async def create_project(newProject:schemas.ProjectNew, db: Session= Depends(get_db)):
    return implementation.create_project(db=db, newProject=newProject)

@router.get("/projects/{projectID}",
            response_model= schemas.Project,
            summary="Returns a single project by ID"
            )
async def get_project(projectID: int, db: Session = Depends(get_db)):
    return implementation.get_project_details(db=db, projectID=projectID)


## DS
@router.get("/ds/{DSid}",
            response_model = schemas.DesignSolution,
            summary="returns a single DS object"
            )
async def get_designSolution(DSid: int, db: Session = Depends(get_db)):
    return implementation.get_DS(db=db, DSid = DSid)


@router.post("/fr/{FRid}/newDS",
            response_model = schemas.DesignSolution,
            summary="creates a new single DS object as a child of FRid"
            )
async def create_designSolution( FRid: int, DSdata: schemas.DSnew, db: Session = Depends(get_db)):
    return implementation.create_DS(db=db, parentID = FRid, newDS= DSdata)

@router.delete("/ds/{DSid}",
            summary="delets a new single DS object by id"
            )
async def delete_designSolution(DSid: int, db: Session = Depends(get_db)):
    return implementation.delete_DS(db= db, DSid = DSid)

@router.put("/ds/{DSid}",
            response_model = schemas.DesignSolution,
            summary="edits an exisitng DS object via DSdata"
            )
async def edit_designSolution(DSid: int, DSdata: schemas.DSnew, db: Session = Depends(get_db)):
    return implementation.edit_DS(DSid = DSid, DSdata = DSdata, db=db)


## FR
@router.get("/fr/{FRid}",
            response_model = schemas.FunctionalRequirement,
            summary="returns a single FR object"
            )
async def get_functionalRequirement(FRid: int, db: Session = Depends(get_db)):
    return implementation.get_FR(db=db, FRid = FRid)


@router.post("/ds/{DSid}/newFR",
            response_model = schemas.FunctionalRequirement,
            summary="creates a new single FR object as a child of DSis",
            description="the json part of the post also contains the DSid - at some point this redundancy needs to be reduced, but how i do not know yet!"
            )
async def create_functionalRequirement( DSid: int, FRdata: schemas.FRNew, db: Session = Depends(get_db)):
    return implementation.create_FR(db=db, parentID = DSid, newFR= FRdata)

@router.delete("/fr/{FRid}",
            summary="delets a new single FR object by id"
            )
async def delete_functionalRequirement(FRid: int, db: Session = Depends(get_db)):
    return implementation.delete_FR(db= db, FRid = FRid)

@router.put("/fr/{FRid}",
            response_model = schemas.DesignSolution,
            summary="edits an exisitng FR object via FRdata"
            )
async def edit_functionalRequirement(FRid: int, FRdata: schemas.DSnew, db: Session = Depends(get_db)):
    return implementation.edit_FR(FRid = FRid, FRdata = FRdata, db=db)

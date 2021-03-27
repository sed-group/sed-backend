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
@router.get("/trees/",
            response_model=List[schemas.Tree],
            summary="Overview over all trees",  
            description="Produces a list of all trees",
            dependencies=[],
            # needs authentication to filter trees by user scope
            )
async def get_all_trees(db: Session = Depends(get_db)):
   return implementation.get_tree_list(db)
   
@router.post("/trees/", 
            response_model=schemas.Tree,
            summary="creating a new tree",
            description="creates a new tree including topLvlDS and returns the tree object",
            )
async def create_tree(newTree:schemas.TreeNew, db: Session= Depends(get_db)):
    return implementation.create_tree(db=db, newTree=newTree)

@router.get("/trees/{treeID}",
            response_model= schemas.Tree,
            summary="Returns a single tree by ID"
            )
async def get_tree(treeID: int, db: Session = Depends(get_db)):
    return implementation.get_tree_details(db=db, treeID=treeID)


## DS
@router.get("/ds/{DSid}",
            response_model = schemas.DesignSolution,
            summary="returns a single DS object with all its children and grandchildren"
            )
async def get_designSolutionTree(DSid: int, db: Session = Depends(get_db)):
    return implementation.get_DS_with_tree(db=db, DSid = DSid)

# @router.get("/ds/{DSid}",
#             response_model = schemas.DSinfo,
#             summary="returns a single DS object"
#             )
# async def get_designSolutionInfo(DSid: int, db: Session = Depends(get_db)):
#     return implementation.get_DS_info(db=db, DSid = DSid)


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
            response_model = schemas.FunctionalRequirement,
            summary="edits an exisitng FR object via FRdata"
            )
async def edit_functionalRequirement(FRid: int, FRdata: schemas.FRNew, db: Session = Depends(get_db)):
    return implementation.edit_FR(FRid = FRid, FRdata = FRdata, db=db)


## DP
@router.get("/dp/{DPid}",
            response_model = schemas.DesignParameter,
            summary="returns a single DP object"
            )
async def get_designParameter(DPid: int, db: Session = Depends(get_db)):
    return implementation.get_DP(db=db, DPid = DPid)

@router.post("/ds/{DSid}/newDP",
            response_model = schemas.DesignParameter,
            summary="creates a new DP object as a child of DSid",
            description="the json part of the post also contains the DSid - at some point this redundancy needs to be reduced, but how i do not know yet!; Furthermore there is redundancy in the treeID"
            )
async def create_designParameter( DSid: int, DPdata: schemas.DPnew, db: Session = Depends(get_db)):
    return implementation.create_DP(db=db, parentID = DSid, newDP= DPdata)

@router.delete("/dp/{DPid}",
            summary="delets a DP object by id"
            )
async def delete_designParameter(DPid: int, db: Session = Depends(get_db)):
    return implementation.delete_DP(db= db, DPid = DPid)

@router.put("/dp/{DPid}",
            response_model = schemas.DesignParameter,
            summary="edits an exisitng DP object via DPdata"
            )
async def edit_designParameter(DPid: int, DPdata: schemas.DPnew, db: Session = Depends(get_db)):
    return implementation.edit_DP(DPid = DPid, DPdata = DPdata, db=db)
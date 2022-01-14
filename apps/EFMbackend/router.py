from fastapi import APIRouter, Depends, Security
# from sqlalchemy.orm import Session
from typing import List

# database
from mysql.connector.pooling import PooledMySQLConnection
from apps.core.db import get_connection

# EFM modules
# from apps.EFMbackend.database import SessionLocal
import apps.EFMbackend.implementation as implementation
import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.algorithms as algorithms

# authentication / security
from apps.core.users.models import User
from apps.core.authentication.utils import get_current_active_user
from apps.core.projects.dependencies import ProjectAccessChecker, SubProjectAccessChecker
from apps.core.projects.models import AccessLevel

# sub-module-routers
# from apps.EFMbackend.parameters.router import router as param_router

router = APIRouter()

EFM_APP_SID = 'MOD.EFM'


## TREES
@router.get("/trees/",
            response_model=List[schemas.TreeInfo],
            summary="Overview over all EFM trees",  
            description="Produces a list of all trees",
            )
async def get_all_trees(current_user: User = Depends(get_current_active_user)):
    return implementation.get_tree_list_of_user(current_user.id)
   
@router.post("/{project_id}/newTree/", 
            response_model=schemas.TreeInfo,
            summary="creating a new tree",
            description="creates a new tree including topLvlDS and returns the tree object. Alsoc creates a new subproject in project_id",
            dependencies=[Depends(ProjectAccessChecker(AccessLevel.list_can_edit()))]
            )
async def create_tree(project_id: int, new_tree:schemas.TreeNew, current_user: User = Depends(get_current_active_user)):
    return implementation.create_tree(project_id = project_id, new_tree=new_tree, user_id = current_user.id)

@router.get("/trees/{native_project_id}",
            response_model= schemas.TreeInfo,
            summary="Returns a single tree by ID",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_tree(native_project_id: int):
    return implementation.get_tree_details(tree_id=native_project_id)

@router.delete("/trees/{native_project_id}",
            response_model=int,
            summary="Deletes a single tree by ID",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def delete_tree(native_project_id: int):
    return implementation.delete_tree(tree_id=native_project_id)

@router.put("/trees/{native_project_id}",
            response_model= schemas.TreeInfo,
            summary="edits the header info of a tree (e.g. name, description) and returns a info object containing only header info",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_tree(native_project_id: int, tree_data: schemas.TreeNew,):
    return implementation.edit_tree(
        tree_id=native_project_id,
        tree_data = tree_data
    )

@router.get("/trees/{native_project_id}/data",
            response_model= schemas.TreeData,
            summary="Returns all information in a tree as a big json dump",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_tree_data(native_project_id: int):
    return implementation.get_tree_data(tree_id = native_project_id)


# CONCEPTS
@router.get("/trees/{native_project_id}/instantiate",
            response_model= List[schemas.Concept],
            summary = "generates all concepts of a tree and returns a list of them -WIP-",
            description = "Executes the instantiation of all possible concepts of a tree and returns them as a list. Computationally expensive!",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def generate_all_concepts(native_project_id: int):
    with get_connection() as db: 
        await implementation.run_instantiation(db = db, tree_id = native_project_id)
        return implementation.get_all_concepts(db = db, tree_id = native_project_id)

@router.get("/trees/{native_project_id}/concepts",
            response_model= List[schemas.Concept],
            summary = "returns all concepts without regenerating them",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_all_concepts(native_project_id: int):
    with get_connection() as db:
        return implementation.get_all_concepts(db = db, tree_id = native_project_id)

@router.get("/{native_project_id}/concepts/{concept_id}",
            response_model= schemas.Concept,
            summary = "returns one concept by ID",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_one_concept(concept_id: int):
    return implementation.get_concept(concept_id = concept_id)

@router.put("/{native_project_id}/concepts/{cID}",
            response_model= schemas.Concept,
            summary = "edits one concepts by ID -WIP-",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_concept(concept_id: int, concept_data: schemas.ConceptEdit):
    return implementation.edit_concept(concept_data= concept_data, concept_id = concept_id)

## DS
@router.get("/{native_project_id}/ds/{ds_id}",
            response_model = schemas.DesignSolution,
            summary="returns a single DS object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_designSolutionInfo(ds_id: int):
    with get_connection() as db:
        return implementation.get_DS_info(db = db, ds_id = ds_id)

@router.post("/{native_project_id}/ds/new",
            response_model = schemas.DesignSolution,
            summary="creates a new single DS object as a child of fr_id",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def create_designSolution(ds_data: schemas.DSnew):
    with get_connection() as db:
        return implementation.create_DS(db = db, new_ds= ds_data)

@router.delete("/{native_project_id}/ds/{ds_id}",
            summary="delets a new single DS object by id",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def delete_designSolution(ds_id: int):
    with get_connection() as db:
        return implementation.delete_DS(db = db, ds_id = ds_id)

@router.put("/{native_project_id}/ds/{ds_id}",
            response_model = schemas.DesignSolution,
            summary="edits an exisitng DS object via ds_data",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_designSolution(ds_id: int, ds_data: schemas.DSnew):
    with get_connection() as db:
        return implementation.edit_DS(
            db = db,
            ds_id = ds_id,
            ds_data = ds_data,
            )

@router.put("/{native_project_id}/ds/{ds_id}/isb/",
            response_model = schemas.DesignSolution,
            summary = "sets new parent to DS",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def new_parent_designSolution(ds_id: int, new_parent_id: int):
    with get_connection() as db:
        return implementation.new_parent_DS(db = db, ds_id= ds_id, fr_id= new_parent_id)


## FR
@router.get("/{native_project_id}/fr/{fr_id}",
            response_model = schemas.FunctionalRequirement,
            summary="returns a single FR object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_functionalRequirement(fr_id: int):
    return implementation.get_FR_info(fr_id = fr_id)

@router.post("/{native_project_id}/fr/new",
            response_model = schemas.FunctionalRequirement,
            summary="creates a new single FR object as a child of DSis",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def create_functionalRequirement(fr_data: schemas.FRnew):
    return implementation.create_FR(fr_new= fr_data)

@router.delete("/{native_project_id}/fr/{fr_id}",
            summary="delets a new single FR object by id",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def delete_functionalRequirement(fr_id: int):
    return implementation.delete_FR(fr_id = fr_id)

@router.put("/{native_project_id}/fr/{fr_id}",
            response_model = schemas.FunctionalRequirement,
            summary="edits an exisitng FR object via fr_data",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_functionalRequirement(fr_id: int, fr_data: schemas.FRnew):
    with get_connection() as db:
        return implementation.edit_FR(fr_id = fr_id, fr_data = fr_data)

@router.put("/{native_project_id}/fr/{fr_id}/rf/",
            response_model = schemas.FunctionalRequirement,
            summary = "sets new parent to FR",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def new_parent_functionalRequirement(fr_id: int, new_parent_id: int):
    return implementation.new_parent_FR(fr_id= fr_id, ds_id= new_parent_id)


# iw 
@router.get("/{native_project_id}/iw/{iw_id}",
            response_model = schemas.InteractsWith,
            summary="returns a single iw object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_interactsWith(iw_id: int):
    with get_connection() as db:
        return implementation.get_IW(db=db, iw_id = iw_id)

@router.post("/{native_project_id}/iw/new",
            response_model = schemas.InteractsWith,
            summary="creates a new iw object via iw_data (json) ",
            description="creates a new interactsWith object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def create_interactsWith(iw_data: schemas.IWnew):
    with get_connection() as db:
     return implementation.create_IW(db=db, iw_new= iw_data)

@router.delete("/{native_project_id}/iw/{iw_id}",
            summary="deletes an iw object by id ",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def delete_interactsWith(iw_id: int):
    with get_connection() as db:
        return implementation.delete_IW(db=db, iw_id = iw_id)

@router.put("/{native_project_id}/iw/{iw_id}",
            response_model = schemas.InteractsWith,
            summary="edits an existing iw object via iw_data (json)",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_interactsWith(iw_id: int, iw_data: schemas.IWedit):
    with get_connection() as db:
        return implementation.edit_IW(db=db, iw_id= iw_id, iw_data=iw_data)

# constraints
@router.get("/{native_project_id}/c/{c_id}",
            response_model = schemas.Constraint,
            summary="returns a single constraint object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_read(), EFM_APP_SID))]
            )
async def get_constraint(c_id: int):
    with get_connection() as db:
        return implementation.get_constraint(db = db, c_id = c_id)

@router.post("/{native_project_id}/c/new",
            response_model = schemas.Constraint,
            summary="creates a new constraint object via c_data (json)",
            description="creates a new constraint object",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def create_constraint(c_data: schemas.ConstraintNew):
    with get_connection() as db:
       return implementation.create_constraint(db = db, c_new = c_data)

@router.delete("/{native_project_id}/c/{c_id}",
            summary="deletes a constraint object by id",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def delete_constraint(c_id: int):
    with get_connection() as db:
        return implementation.delete_constraint(db = db,  c_id = c_id)

@router.put("/{native_project_id}/c/{c_id}",
            response_model = schemas.Constraint,
            summary="edits an existing constraint object via iw_data (json)",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def edit_constraint(c_id: int, c_data: schemas.ConstraintNew):
    with get_connection() as db:
        return implementation.edit_constraint(db = db, c_id = c_id, c_data = c_data)

@router.put("/{native_project_id}/c/{c_id}/icb/",
            response_model = schemas.Constraint,
            summary = "sets new parent to a constraint",
            dependencies=[Depends(SubProjectAccessChecker(AccessLevel.list_can_edit(), EFM_APP_SID))]
            )
async def new_parent_constraint(ds_id: int, new_parent_id: int):
    with get_connection() as db:
        return implementation.new_parent_DS(db = db, ds_id= ds_id, fr_id= new_parent_id)


# router.include_router(param_router, prefix="/param", tags=['EF-M parameters'])
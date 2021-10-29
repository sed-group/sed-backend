from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import json

# efm modules import
import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.storage as storage
import apps.EFMbackend.algorithms as algorithms

from apps.EFMbackend.exceptions import *
from apps.EFMbackend.database import get_connection as efm_connection
from apps.EFMbackend.utils import not_yet_implemented

# imports from EF-M sub-modules
from apps.EFMbackend.parameters.schemas import DesignParameter
from apps.EFMbackend.parameters.storage import get_DP_all

# imports from core
from apps.core.db import get_connection as core_connection
import apps.core.projects.storage as proj_storage
import apps.core.projects.models as proj_models

EFM_APP_SID = 'MOD.EFM'

#### TREES
def get_tree_list_of_user(db: Session, user_id: int, limit:int = 100, offset:int = 0) \
    -> List[schemas.TreeInfo]:
    '''
    list of all tree objects from DB
    where user has access to

    :param db: efm database connection
    :param userID: core user id
    :param limit: pagination length
    :param offset: pagination offset
    :return: list of schemas.TreeInfo
    '''
    with core_connection() as con:
        subproject_list = proj_storage.db_get_user_subprojects_with_application_sid(con, user_id, EFM_APP_SID)

    tree_list = []
    counter = offset    # For pagination
    # print(subproject_list)
    while len(subproject_list) > counter and counter < (offset+limit):
        # print(f'fetching subproject tree with id{subproject_list[counter].native_project_id}')
        try: 
            tree = storage.get_efm_object(db, 'tree', subproject_list[counter].native_project_id)
            tree_list.append(tree)
        except:
            print(f'could not find subproject tree with id {subproject_list[counter].native_project_id}')
        counter = counter + 1

    # tree_list = storage.get_efm_objects_all_of_tree(db, 'tree', 0, limit, offset)
    tree_info_list = []

    # conversion to schemas.TreeInfo
    for t in tree_list:
        t_info = schemas.TreeInfo(**t.dict())
        tree_info_list.append(t_info)

    return tree_info_list

def create_tree(db: Session, project_id:int, new_tree: schemas.TreeNew, user_id: int):
    '''
        creates one new tree based on schemas.treeNew
        creates a new subproject in project_id 
        creates a top-level DS and associates its ID to tree.top_level_ds_id
    '''
    # first check whether project exists
    with core_connection() as con:
        try:
            proj_storage.db_get_project_exists(con, project_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No project with ID {project_id} could be found"
            )

        # create tree without DS:
        the_tree = storage.new_efm_object(db, 'tree', new_tree)

        # manufacture a top-levelDS:
        top_ds = schemas.DSnew(
            name=new_tree.name, 
            description="Top-level DS", 
            tree_id = the_tree.id, 
            is_top_level_ds = True
            )

        # creating the DS in the DB
        top_ds = storage.new_efm_object(db, 'DS', top_ds)

        # setting the tree topLvlDS
        the_tree = storage.tree_set_top_lvl_ds(db, the_tree.id, top_ds.id)

        # create new sub-project on core level:
        new_subproject_data = proj_models.SubProjectPost(
            application_sid = EFM_APP_SID,
            native_project_id = the_tree.id,
        )
        
        new_subproject = proj_storage.db_post_subproject(
            connection = con, 
            subproject = new_subproject_data, 
            current_user_id = user_id,
            project_id = project_id
            )
        con.commit()

    the_tree = storage.tree_set_subproject(db, the_tree.id, new_subproject.id)

    print(the_tree)
    print(new_subproject)


    return the_tree

def edit_tree(db:Session, tree_id: int, tree_data: schemas.TreeNew):
    return storage.edit_efm_object(db, 'tree', tree_id, tree_id)

def get_tree_details(db: Session, tree_id: int):
    ''' 
        returns a tree object with all details
        returns a schemas.Tree
    '''
    the_tree = storage.get_efm_object(db, 'tree', tree_id)
    return the_tree

def delete_tree(db: Session, tree_id: int):
    '''
        deletes tree based on id 
        also deletes the related subproject in core
    '''
    storage.delete_efm_object(
        db = db,
        efm_object_type = 'tree', 
        object_id = tree_id
        )

    # deleting the respective sub-project:
    with core_connection() as con:
        subproject = proj_storage.db_get_subproject_native(
            connection = con, 
            application_sid = EFM_APP_SID, 
            native_project_id = tree_id
            )
        proj_storage.db_delete_subproject(
            connection = con, 
            project_id = subproject.project_id,
            subproject_id = subproject.id, 
            )

        return True

def get_tree_data(db: Session, tree_id: int, depth:int=0):
    '''
    returns a list of all obejcts related to a specific tree
    depth = 0 makes it return _all_ objects - can be quite big then!
    however, there is no sorting applied to the returned objects, so it is difficult to know which elements you get back...
    '''

    the_tree = storage.get_efm_object(db, 'tree', tree_id)

    tree_data = schemas.TreeData(**the_tree.dict())

    # fetch DS
    all_ds = storage.get_efm_objects_all_of_tree(db, 'DS', tree_id, depth)
    # all_ds = db.query(models.DesignSolution).filter(models.DesignSolution.tree_id == tree_id).all()
    for ds in all_ds:
        pydantic_ds_tree = schemas.DesignSolution.from_orm(ds)
        the_ds_info = schemas.DSinfo(**pydantic_ds_tree.dict())
        the_ds_info.update(pydantic_ds_tree)
        tree_data.ds.append(the_ds_info)

    # fetch FR
    all_fr = storage.get_efm_objects_all_of_tree(db, 'FR', tree_id, depth)
    for fr in all_fr:
        pydantic_fr_tree = schemas.FunctionalRequirement.from_orm(fr)
        the_fr_info = schemas.FRinfo(**pydantic_fr_tree.dict())
        the_fr_info.update(pydantic_fr_tree)
        tree_data.fr.append(the_fr_info)

    # fetch iw
    all_iw = storage.get_efm_objects_all_of_tree(db, 'iw', tree_id, depth)
    tree_data.iw = all_iw

    # fetch DP
    all_dp = get_DP_all(db, tree_id, depth)
    tree_data.dp = all_dp

    # fetch constraints
    all_c = storage.get_efm_objects_all_of_tree(db, 'c', tree_id, depth)
    tree_data.c = all_c

    return tree_data

### CONCEPTS
def get_all_concepts(db: Session, tree_id: int, limit:int=100, offset: int = 0):
    '''
    returns a list of all concepts of the tree identified via tree_id
    '''
    return storage.get_efm_objects_all_of_tree(db, 'concept', tree_id, limit, offset)

def get_concept(db: Session, cID: int):
    return storage.get_efm_object(db, 'concept', cID)

def edit_concept(db: Session, cID: int, cData: schemas.ConceptEdit):
    return storage.edit_efm_object(db, 'concept', cID, cData)

def get_concept_tree(db: Session, cID: int):
    '''
    takes the tree of which the concept has been instantiated
    and prunes all DS not in the dna
    requires algorithms.prune_child_ds() (cause recursive)
    '''
    the_concept = storage.get_efm_object(db, 'concept', cID)
    the_tree = storage.get_efm_object(db, 'tree', the_concept.tree_id)

    # pruning:
    ds_pruned = algorithms.prune_child_ds(the_tree.topLvlDS, the_concept.dnaList())

    concept_with_tree = schemas.ConceptTree(**the_concept.dict())

    concept_with_tree.topLvlDS = ds_pruned

    return concept_with_tree

### FR
def get_FR_tree(db:Session, fr_id: int):
    ''' 
        returns a FR object with all details
        and the subsequent tree elements
    '''
    return storage.get_efm_object(db, 'FR', fr_id)

def get_FR_info(db:Session, fr_id: int):
    ''' 
        returns a FR object with all details
        but instead of relationships only ids
    ''' 
    the_fr_treeform = storage.get_efm_object(db, 'FR', fr_id)
    the_fr_infoform = schemas.FRinfo(**the_fr_treeform.dict())
    the_fr_infoform.update(the_fr_treeform)

    return the_fr_infoform

def create_FR(db: Session, fr_new: schemas.FRnew):
    '''
        creates new FR based on schemas.FRnew (name, description) 
        associates it to DS with parentID via FR.rf_id ("requires function")
    '''
    # checking if parent exists
    parent_ds = storage.get_efm_object(db, 'DS', fr_new.rf_id)
    # setting tree_id for fetching
    fr_new.tree_id = parent_ds.tree_id
    
    return storage.new_efm_object(db, 'FR', fr_new)
    
def delete_FR(db: Session, fr_id: int):
    '''
        deletes FR based on id 
    '''
    storage.delete_efm_object(db, 'FR', fr_id)

def edit_FR(db: Session, fr_id: int, fr_data: schemas.FRnew):
    '''
        overwrites the data in the FR identified with fr_id with the data from fr_data
        can change parent (i.e. isb), name and description
        tree_id is set through parent; therefore, change of tree is theoretically possible
    '''
    # first we need to set the tree_id, fetched from the parent DS
    parent_ds = storage.get_efm_object(db, 'DS', fr_data.rf_id)
    fr_data.tree_id = parent_ds.tree_id

    return storage.edit_efm_object(db, 'FR', fr_id, fr_data)
    
def newParent_FR(db: Session, fr_id: int, ds_id: int):
    '''
    sets ds_id as new rf_id for FR
    i.e. a change in parent
    '''
    # fetch the FR data
    fr_data = storage.get_efm_object(db, 'FR', fr_id)
    # first we check if the new parent exists
    new_parent_DS = storage.get_efm_object(db, 'DS', ds_id)
    # convert to FRnew object to avoid writing child relations
    fr_data = schemas.FRnew(**fr_data.dict())
    # set new parent ID
    fr_data.rf_id = new_parent_DS.id
    
    # store it
    return storage.edit_efm_object(db, 'FR', fr_id, fr_data)


### DS
def get_DS_with_tree(db:Session, ds_id: int):
    ''' 
        returns a DS object with all details
    '''
    return storage.get_efm_object(db, 'DS', ds_id)

def get_DS_info(db:Session, ds_id: int):
    ''' 
        returns a DS object with all details
        but instead of relationships only ids
    '''
    the_ds_treeform = storage.get_efm_object(db, 'DS', ds_id)

    the_ds_infoform = schemas.DSinfo(**the_ds_treeform.dict())
    the_ds_infoform.update(the_ds_treeform)

    return the_ds_infoform

def create_DS(db: Session, new_ds: schemas.DSnew):
    '''
        creates new DS based on schemas.DSnew (name, description) 
        associates it to 
    '''
    # first we need to set the tree_id, fetched from the parent FR
    parent_fr = storage.get_efm_object(db, 'FR', new_ds.isb_id)
    new_ds.tree_id = parent_fr.tree_id

    return storage.new_efm_object(db, 'DS', new_ds)
    
def delete_DS(db: Session, ds_id: int):
    '''
        deletes DS based on id 
    '''
    return storage.delete_efm_object(db, 'DS', ds_id)

def edit_DS(db: Session, ds_id: int, ds_data: schemas.DSnew):
    '''
        overwrites the data in the DS identified with ds_id with the data from DSnew
        can change parent (i.e. isb), name and description
        checks whether the new parent FR is in the same tree
        cannot change tree! (tree_id)
    '''
    # first we need to set (correct?) the tree_id, fetched from the parent FR
    parent_fr = storage.get_efm_object(db, 'FR', ds_data.isb_id)
    ds_data.tree_id = parent_fr.tree_id

    return storage.edit_efm_object(db, 'DS', ds_id, ds_data)

def newParent_DS(db: Session, ds_id: int, fr_id: int):
    '''
    sets fr_id as new isb_id for DS
    i.e. a change in parent
    '''
    # fetch the DS data
    ds_data = storage.get_efm_object(db, 'DS', ds_id)
    
    # first we check if the new parent exists
    new_parent_FR = storage.get_efm_object(db, 'FR', fr_id)
    # convert to DSnew object to avoid writing child relations
    ds_data = schemas.DSnew(**ds_data.dict())
    # set new parent ID
    ds_data.isb_id = new_parent_FR.id
    
    # store it
    return storage.edit_efm_object(db, 'DS', ds_id, ds_data)




### iw 
def get_IW(db:Session, iw_id: int):
    return storage.get_efm_object(db, 'iw', iw_id)

def create_IW(db: Session,  iw_new: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        but don't have the same parent_fr
            --> this needs to check whether they are _on no level_ in alternative DS; so i'm afraid we need to iterate all the parent DS and check whether one of them are alternatives to each other?? 
            --> NOT IMPLEMENTED
        then commits to DB
    '''

    to_ds = storage.get_efm_object(db, 'DS', iw_new.to_ds_id)
    from_ds = storage.get_efm_object(db, 'DS', iw_new.from_ds_id)

    # checking if we're in the same tree:
    if not to_ds.tree_id == from_ds.tree_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    # setting tree_id since its optional 
    iw_new.tree_id = to_ds.tree_id

    # checking whether we're in the same instance (no share 1st lvl FR parent)
    # --> needs to be extended for any level FR parent!
    if to_ds.isb_id == from_ds.isb_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='DS for an iw need to be in the same concept instance; DS {} and {} are exclusive alternatives'.format(to_ds.name, from_ds.name)
        )

    iw_new.tree_id = to_ds.tree_id

    return storage.new_efm_object(db, 'iw', iw_new)

def delete_IW(db:Session, iw_id: int):
    return storage.delete_efm_object(db, 'iw', iw_id)

def edit_IW(db: Session, iw_id: int, iw_data: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        then commits to DB
    '''
    to_ds = storage.get_efm_object(db, 'DS', iw_data.to_ds_id)
    from_ds = storage.get_efm_object(db, 'DS', iw_data.from_ds_id)

    if not to_ds.tree_id == from_ds.tree_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    iw_data.tree_id = to_ds.tree_id

    return storage.edit_efm_object(db, 'iw', iw_id, iw_data)

## constraints
def get_constraint(db:Session, c_id: int):
    return storage.get_efm_object(db, 'c', c_id)

def create_constraint(db: Session,  c_new: schemas.ConstraintNew):
    '''
        commits new constraint to DB
    '''

    icb_ds = storage.get_efm_object(db, 'DS', c_new.icb_id)

    # setting tree_id since its optional (backwards compatibility ^^)
    c_new.tree_id = icb_ds.tree_id

    return storage.new_efm_object(db, 'c', c_new)

def delete_constraint(db: Session, c_id = int):
    '''
        deletes one constraint from db
        returns true or raises error
    '''
    # check if constraint exists
    constraint = storage.get_efm_object(
        db = db, 
        efm_object_type = 'c',
        object_id = c_id
        )
    return storage.delete_efm_object(
        db = db, 
        efm_object_type = 'c', 
        object_id = constraint.id
        )

def edit_constraint(db: Session, c_id: int, c_data: schemas.ConstraintNew):
    '''
        sets all values of constraint with c_id in db with data of c_data
        returns edited constraint
    '''
    return storage.edit_efm_object(
        db = db,
        efm_object_type = 'c',
        object_id = c_id,
        object_data = c_data
        )
    
    
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
    print(subproject_list)
    while len(subproject_list) > counter and counter < (offset+limit):
        print(f'fetching subproject tree with id{subproject_list[counter].native_project_id}')
        try: 
            tree = storage.get_EFMobject(db, 'tree', subproject_list[counter].native_project_id)
            tree_list.append(tree)
        except:
            print(f'could not find subproject tree with id {subproject_list[counter].native_project_id}')
        counter = counter + 1

    # tree_list = storage.get_EFMobjectAll(db, 'tree', 0, limit, offset)
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
    with core_connection() as con:
        new_subproject = proj_storage.db_post_subproject(
            connection = con, 
            subproject = new_subproject_data, 
            current_user_id = user_id,
            project_id = project_id
            )
    the_tree = storage.tree_set_subproject(db, the_tree.id, new_subproject.id)


    return the_tree

def edit_tree(db:Session, tree_id: int, tree_data: schemas.TreeNew):
    return storage.edit_EFMobject(db, 'tree', tree_id, tree_id)

def get_tree_details(db: Session, tree_id: int):
    ''' 
        returns a tree object with all details
        returns a schemas.Tree
    '''
    the_tree = storage.get_EFMobject(db, 'tree', tree_id)
    return the_tree


def delete_tree(db: Session, tree_id: int):
    '''
        deletes tree based on id 
    '''
    return storage.delete_EFMobject(db, 'tree', tree_id)

def get_tree_data(db: Session, tree_id: int, depth:int=0):
    '''
    returns a list of all obejcts related to a specific tree
    depth = 0 makes it return _all_ objects - can be quite big then!
    however, there is no sorting applied to the returned objects, so it is difficult to know which elements you get back...
    '''

    the_tree = storage.get_EFMobject(db, 'tree', tree_id)

    tree_data = schemas.TreeData(**the_tree.dict())

    # fetch DS
    all_ds = storage.get_EFMobjectAll(db, 'DS', tree_id, depth)
    # all_ds = db.query(models.DesignSolution).filter(models.DesignSolution.tree_id == tree_id).all()
    for ds in all_ds:
        pydantic_ds_tree = schemas.DesignSolution.from_orm(ds)
        the_ds_info = schemas.DSinfo(**pydantic_ds_tree.dict())
        the_ds_info.update(pydantic_ds_tree)
        tree_data.ds.append(the_ds_info)

    # fetch FR
    allFR = storage.get_EFMobjectAll(db, 'FR', tree_id, depth)
    for fr in allFR:
        pydantic_fr_tree = schemas.FunctionalRequirement.from_orm(fr)
        the_fr_info = schemas.FRinfo(**pydantic_fr_tree.dict())
        the_fr_info.update(pydantic_fr_tree)
        tree_data.fr.append(the_fr_info)

    # fetch iw
    all_iw = storage.get_EFMobjectAll(db, 'iw', tree_id, depth)
    tree_data.iw = all_iw

    # fetch DP
    all_dp = get_DP_all(db, tree_id, depth)
    tree_data.dp = all_dp

    return tree_data

### CONCEPTS
def get_all_concepts(db: Session, tree_id: int, limit:int=100, offset: int = 0):
    '''
    returns a list of all concepts of the tree identified via tree_id
    '''
    return storage.get_EFMobjectAll(db, 'concept', tree_id, limit, offset)

def get_concept(db: Session, cID: int):
    return storage.get_EFMobject(db, 'concept', cID)

def edit_concept(db: Session, cID: int, cData: schemas.ConceptEdit):
    return storage.edit_EFMobject(db, 'concept', cID, cData)

def get_concept_tree(db: Session, cID: int):
    '''
    takes the tree of which the concept has been instantiated
    and prunes all DS not in the dna
    requires algorithms.prune_child_ds() (cause recursive)
    '''
    theConcept = storage.get_EFMobject(db, 'concept', cID)
    the_tree = storage.get_EFMobject(db, 'tree', theConcept.tree_id)

    # pruning:
    prunedDS = algorithms.prune_child_ds(theTree.topLvlDS, theConcept.dnaList())

    conceptWithTree = schemas.ConceptTree(**theConcept.dict())

    conceptWithTree.topLvlDS = prunedDS

    return conceptWithTree

### FR
def get_FR_tree(db:Session, FRid: int):
    ''' 
        returns a FR object with all details
        and the subsequent tree elements
    '''
    return storage.get_EFMobject(db, 'FR', FRid)

def get_FR_info(db:Session, FRid: int):
    ''' 
        returns a FR object with all details
        but instead of relationships only ids
    ''' 
    theTreeFR = storage.get_EFMobject(db, 'FR', FRid)
    theInfoFR = schemas.FRinfo(**theTreeFR.dict())
    theInfoFR.update(theTreeFR)

    return theInfoFR


def create_FR(db: Session, newFR: schemas.FRNew):
    '''
        creates new FR based on schemas.FRnew (name, description) 
        associates it to DS with parentID via FR.rfID ("requires function")
    '''
    # first we need to set the tree_id, fetched from the parent DS
    parentDS = storage.get_EFMobject(db, 'DS', newFR.rfID)
    newFR.tree_id = parentDS.tree_id

    return storage.new_efm_object(db, 'FR', newFR)
    
def delete_FR(db: Session, FRid: int):
    '''
        deletes FR based on id 
    '''
    storage.delete_EFMobject(db, 'FR', FRid)

def edit_FR(db: Session, FRid: int, FRdata: schemas.FRNew):
    '''
        overwrites the data in the FR identified with FRid with the data from FRdata
        can change parent (i.e. isb), name and description
        tree_id is set through parent; therefore, change of tree is theoretically possible
    '''
    # first we need to set the tree_id, fetched from the parent DS
    parentDS = storage.get_EFMobject(db, 'DS', FRdata.rfID)
    FRdata.tree_id = parentDS.tree_id

    return storage.edit_EFMobject(db, 'FR', FRid, FRdata)
    
def newParent_FR(db: Session, FRid: int, DSid: int):
    '''
    sets DSid as new rfID for FR
    i.e. a change in parent
    '''
    # fetch the FR data
    fr_data = storage.get_EFMobject(db, 'FR', FRid)
    # first we check if the new parent exists
    new_parent_DS = storage.get_EFMobject(db, 'DS', DSid)
    # set new parent ID
    fr_data.rfID = new_parent_DS.id
    
    # store it
    return storage.edit_EFMobject(db, 'FR', FRid, fr_data)


### DS
def get_DS_with_tree(db:Session, DSid: int):
    ''' 
        returns a DS object with all details
    '''
    return storage.get_EFMobject(db, 'DS', DSid)

def get_DS_info(db:Session, DSid: int):
    ''' 
        returns a DS object with all details
        but instead of relationships only ids
    '''
    theDStree = storage.get_EFMobject(db, 'DS', DSid)

    theInfoDS = schemas.DSinfo(**theDStree.dict())
    theInfoDS.update(theDStree)

    return theInfoDS

def create_DS(db: Session, newDS: schemas.DSnew):
    '''
        creates new DS based on schemas.DSnew (name, description) 
        associates it to 
    '''
    # first we need to set the tree_id, fetched from the parent FR
    parentFR = storage.get_EFMobject(db, 'FR', newDS.isbID)
    newDS.tree_id = parentFR.tree_id

    return storage.new_efm_object(db, 'DS', newDS)
    
def delete_DS(db: Session, DSid: int):
    '''
        deletes DS based on id 
    '''
    return storage.delete_EFMobject(db, 'DS', DSid)

def edit_DS(db: Session, DSid: int, DSdata: schemas.DSnew):
    '''
        overwrites the data in the DS identified with DSid with the data from DSnew
        can change parent (i.e. isb), name and description
        checks whether the new parent FR is in the same tree
        cannot change tree! (tree_id)
    '''
    # first we need to set (correct?) the tree_id, fetched from the parent FR
    parentFR = storage.get_EFMobject(db, 'FR', DSdata.isbID)
    DSdata.tree_id = parentFR.tree_id

    return storage.edit_EFMobject(db, 'DS', DSid, DSdata)

def newParent_DS(db: Session, DSid: int, FRid: int):
    '''
    sets FRid as new isbID for DS
    i.e. a change in parent
    '''
    # fetch the DS data
    ds_data = storage.get_EFMobject(db, 'DS', DSid)
    # first we check if the new parent exists
    new_parent_FR = storage.get_EFMobject(db, 'FR', FRid)
    # set new parent ID
    ds_data.isbID = new_parent_FR.id
    
    # store it
    return storage.edit_EFMobject(db, 'DS', DSid, ds_data)




### iw todo!! 
def get_IW(db:Session, IWid: int):
    return storage.get_EFMobject(db, 'iw', IWid)

def create_IW(db: Session,  newIW: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        but don't have the same parentFR
            --> this needs to check whether they are _on no level_ in alternative DS; so i'm afraid we need to iterate all the parent DS and check whether one of them are alternatives to each other?? 
            --> NOT IMPLEMENTED
        then commits to DB
    '''

    toDS = storage.get_EFMobject(db, 'DS', newIW.toDsID)
    fromDS = storage.get_EFMobject(db, 'DS', newIW.fromDsID)

    # checking if we're in the same tree:
    if not toDS.tree_id == fromDS.tree_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    # setting tree_id since its optional 
    newIW.tree_id = toDS.tree_id

    # checking whether we're in the same instance (no share 1st lvl FR parent)
    # --> needs to be extended for any level FR parent!
    if toDS.isbID == fromDS.isbID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='DS for an iw need to be in the same concept instance; DS {} and {} are exclusive alternatives'.format(toDS.name, fromDS.name)
        )

    newIW.tree_id = toDS.tree_id

    return storage.new_efm_object(db, 'iw', newIW)

def delete_IW(db:Session, IWid: int):
    return storage.delete_EFMobject(db, 'iw', IWid)

def edit_IW(db: Session, IWid: int, IWdata: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        then commits to DB
    '''
    toDS = storage.get_EFMobject(db, 'DS', IWdata.toDsID)
    fromDS = storage.get_EFMobject(db, 'DS', IWdata.fromDsID)

    if not toDS.tree_id == fromDS.tree_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    IWdata.tree_id = toDS.tree_id

    return storage.edit_EFMobject(db, 'iw', IWid, IWdata)


#  {
#     "name":"TestFR",
#     "description":"just a test?",
#     "tree_id":2,
#     "rfID":2,
#     "id":1,
#     "tree": {
#         "name": "foobar",
#         "description":"The Foo Barters",
#         "id":2,
#         "concepts":[],
#         "fr":[],
#         "ds":[],
#         "top_level_ds_id":2
#         },
#     "is_solved_by":[
#         {"name":"ds child",
#         "description":"child test 1",
#         "tree_id":2,
#         "isbID":1,
#         "id":4,
#         "requires_functions":[],
#         "tree":{
#             "name":"foobar",
#             "description":"The Foo Barters",
#             "id":2,"concepts":[],
#             "fr":[],
#             "ds":[],
#             "top_level_ds_id":2
#             },
#         "is_top_level_DS":false}
#     ]
# }
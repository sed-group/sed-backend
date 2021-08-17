from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List
import json

import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.storage as storage
import apps.EFMbackend.algorithms as algorithms

from apps.EFMbackend.exceptions import *
# from apps.EFMbackend.database import get_connection

from apps.EFMbackend.utils import not_yet_implemented

# imports from EF-M sub-modules
from apps.EFMbackend.parameters.schemas import DesignParameter
from apps.EFMbackend.parameters.storage import get_DP_all


#### TREES
def get_tree_list(db: Session, limit:int = 100, offset:int = 0):
    '''
    list of all tree objects from DB
    '''
    return storage.get_EFMobjectAll(db, 'tree', 0, limit, offset)

def create_tree(db: Session, newTree = schemas.TreeNew):
    '''
        creates one new tree based on schemas.treeNew 
        creates a top-level DS and associates its ID to tree.topLvlDSid
    '''
    # create tree without DS:
    
    theTree = storage.new_EFMobject(db, 'tree', newTree)

    # manufacture a top-levelDS:
    topDS = schemas.DSnew(
        name=newTree.name, 
        description="Top-level DS", 
        treeID = theTree.id, 
        is_top_level_DS = True
        )

    # creating the DS in the DB
    topDS = storage.new_EFMobject(db, 'DS', topDS)

    # setting the tree topLvlDS
    theTree = storage.tree_set_topLvlDs(db, theTree.id, topDS.id)
    return theTree

def edit_tree(db:Session, treeID: int, treeData: schemas.TreeNew):
    return storage.edit_EFMobject(db, 'tree', treeID, treeID)

def get_tree_details(db: Session, treeID: int):
    ''' 
        returns a tree object with all details
        returns a schemas.Tree
    '''
    theTree = storage.get_EFMobject(db, 'tree', treeID)
    return theTree


def delete_tree(db: Session, treeID: int):
    '''
        deletes tree based on id 
    '''
    return storage.delete_EFMobject(db, 'tree', treeID)

def get_tree_data(db: Session, treeID: int, depth:int=0):
    '''
    returns a list of all obejcts related to a specific tree
    depth = 0 makes it return _all_ objects - can be quite big then!
    however, there is no sorting applied to the returned objects, so it is difficult to know which elements you get back...
    '''

    theTree = storage.get_EFMobject(db, 'tree', treeID)

    treeData = schemas.TreeData(**theTree.dict())

    # fetch DS
    allDS = storage.get_EFMobjectAll(db, 'DS', treeID, depth)
    # allDS = db.query(models.DesignSolution).filter(models.DesignSolution.treeID == treeID).all()
    for ds in allDS:
        pydanticDStree = schemas.DesignSolution.from_orm(ds)
        theDSinfo = schemas.DSinfo(**pydanticDStree.dict())
        theDSinfo.update(pydanticDStree)
        treeData.ds.append(theDSinfo)

    # fetch FR
    allFR = storage.get_EFMobjectAll(db, 'FR', treeID, depth)
    for fr in allFR:
        pydanticFRtree = schemas.FunctionalRequirement.from_orm(fr)
        theFRinfo = schemas.FRinfo(**pydanticFRtree.dict())
        theFRinfo.update(pydanticFRtree)
        treeData.fr.append(theFRinfo)

    # fetch iw
    allIW = storage.get_EFMobjectAll(db, 'iw', treeID, depth)
    treeData.iw = allIW

    # fetch DP
    allDP = get_DP_all(db, treeID, depth)
    treeData.dp = allDP

    return treeData

### CONCEPTS
def get_all_concepts(db: Session, treeID: int, limit:int=100, offset: int = 0):
    '''
    returns a list of all concepts of the tree identified via treeID
    '''
    return storage.get_EFMobjectAll(db, 'concept', treeID, limit, offset)

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
    theTree = storage.get_EFMobject(db, 'tree', theConcept.treeID)

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
    # first we need to set the treeID, fetched from the parent DS
    parentDS = storage.get_EFMobject(db, 'DS', newFR.rfID)
    newFR.treeID = parentDS.treeID

    return storage.new_EFMobject(db, 'FR', newFR)
    
def delete_FR(db: Session, FRid: int):
    '''
        deletes FR based on id 
    '''
    storage.delete_EFMobject(db, 'FR', FRid)

def edit_FR(db: Session, FRid: int, FRdata: schemas.FRNew):
    '''
        overwrites the data in the FR identified with FRid with the data from FRdata
        can change parent (i.e. isb), name and description
        treeID is set through parent; therefore, change of tree is theoretically possible
    '''
    # first we need to set the treeID, fetched from the parent DS
    parentDS = storage.get_EFMobject(db, 'DS', FRdata.rfID)
    FRdata.treeID = parentDS.treeID

    return storage.edit_EFMobject(db, 'FR', FRid, FRdata)
    
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
    # first we need to set the treeID, fetched from the parent FR
    parentFR = storage.get_EFMobject(db, 'FR', newDS.isbID)
    newDS.treeID = parentFR.treeID

    return storage.new_EFMobject(db, 'DS', newDS)
    
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
        cannot change tree! (treeID)
    '''
    # first we need to set the treeID, fetched from the parent FR
    parentFR = storage.get_EFMobject(db, 'FR', DSdata.isbID)
    DSdata.treeID = parentFR.treeID

    return storage.edit_EFMobject(db, 'DS', DSid, DSdata)

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
    if not toDS.treeID == fromDS.treeID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    # checking whether we're in the same instance (no share 1st lvl FR parent)
    # --> needs to be extended for any level FR parent!
    if toDS.isbID == fromDS.isbID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='DS for an iw need to be in the same instance; DS {} and {} share a parent FR'.format(toDS.name, fromDS.name)
        )


    newIW.treeID = toDS.treeID

    return storage.new_EFMobject(db, 'iw', newIW)

def delete_IW(db:Session, IWid: int):
    return storage.delete_EFMobject(db, 'iw', IWid)

def edit_IW(db: Session, IWid: int, IWdata: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        then commits to DB
    '''
    toDS = storage.get_EFMobject(db, 'DS', IWdata.toDsID)
    fromDS = storage.get_EFMobject(db, 'DS', IWdata.fromDsID)

    if not toDS.treeID == fromDS.treeID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both DS for an iw need to be in the same tree"
        )

    IWdata.treeID = toDS.treeID

    return storage.edit_EFMobject(db, 'iw', IWid, IWdata)


#  {
#     "name":"TestFR",
#     "description":"just a test?",
#     "treeID":2,
#     "rfID":2,
#     "id":1,
#     "tree": {
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
#         "treeID":2,
#         "isbID":1,
#         "id":4,
#         "requires_functions":[],
#         "tree":{
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
from sqlalchemy.orm import Session, lazyload, eagerload
from fastapi import HTTPException, status


import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas
from apps.EFMbackend.exceptions import *

# from apps.core.db import get_connection
# from apps.EFMbackend.models import *
# from apps.EFMbackend.exceptions import *
# import apps.EFMbackend.storage as storage


def not_yet_implemented():
    ''' 
    dummy function for not yet implemented API functions 
    '''
    raise HTTPException(
            status_code=status.HTTP_425_TOO_EARLY,
            detail="API point has not been realised yet, we appologize"
        )

#### TREES
def get_tree_list(db: Session, limit:int = 100, offset:int = 0):
    '''
    list of all tree objects from DB
    '''
    return db.query(models.Tree).offset(offset).limit(limit).all()

def create_tree(db: Session, newTree = schemas.TreeNew):
    '''
        creates one new tree based on schemas.treeNew 
        creates a top-level DS and associates its ID to tree.topLvlDSid
    '''
    # create tree without DS:
    theTree = models.Tree(**newTree.dict())
    db.add(theTree)
    db.commit()

    # create a top-levelDS:
    topDS = models.DesignSolution(name=newTree.name, description="Top-level DS", treeID = theTree.id, is_top_level_DS = True)
    db.add(topDS)
    db.commit()

    # setting the tree topLvlDS
    theTree.topLvlDSid = topDS.id
    db.commit()

    return theTree

def get_tree_details(db:Session, treeID: int):
    ''' 
        returns a tree object with all details
    '''
    try:
        theTree = db.query(models.Tree).filter(models.Tree.id == treeID).first()
        if theTree:
            return theTree
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tree with ID {} does not exist.".format(treeID)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree with ID {} does not exist.".format(treeID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="treeID needs to be an integer"
        )

def delete_tree(db: Session, treeID: int):
    '''
        deletes tree based on id 
    '''
    try:
        db.query(models.Tree).filter(models.Tree.id == treeID).delete()
        db.commit()
        return True
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tree with ID {} does not exist.".format(treeID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="treeID needs to be an integer"
        )

def get_tree_data(db: Session, treeID: int):
    return not_yet_implemented()

### CONCEPTS
def run_instantiation(db: Session, treeID: int):
    
    # fetch the old concepts, if available:
    allOldConcepts = get_all_concepts(db, treeID) # will get deleted later
    allNewConcepts = []                           # will get added later

    theTree = get_tree_details(db, treeID)

    allDna = theTree.topLvlDS.alternativeConfigurations()

    conceptCounter = allOldConcepts.len()

    for dna in allDna:
        
        dnaString = json.dumps(dna)

        # check if already exists:
        for oldC in allOldConcepts:
            if oldC.dna == dna:
                # remove from list so it won't get deleted:
                allOldConcepts.remove(oldC)
                # and we don't need to create a new object for it, so we jump
                next()

        newConcept = models.Concept()
        newConcept.name = f"Concept {conceptCounter}"
        newConcept.dna = dnaString
        newConcept.treeID = treeID

        allNewConcepts.append(newConcept)
        conceptCounter = conceptCounter + 1

    # add new concepts:
    for nC in allNewConcepts:
        db.add(nC)
    
    # delete old concepts:
    for oC in allOldConcepts:
        db.query(models.Concept).filter(models.Concept.id == oC.id).delete()

    db.commit()


    return not_yet_implemented()

def get_all_concepts(db: Session, treeID: int):
    '''
    returns a list of all concepts of the tree identified via treeID
    '''
    return db.query(models.Concept).filter(models.Concept.treeID == treeID).all()

def get_concept(db: Session, cID: int):
    return not_yet_implemented()

def edit_concept(db: Session, cID: int, cData: schemas.ConceptEdit):
    return not_yet_implemented()

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

    # check for same tree 
    try:
        theParent = db.query(models.DesignSolution).filter(models.DesignSolution.id == parentID).first()
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new FR; parent DS with ID {} cannot be found.".format(parentID)
        )
    
    if theParent.treeID != newFR.treeID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new FR; parent DS is in another tree! parentTreeID: {}, FRtreeID: {}".format(theParent.treeID, newFR.treeID)
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
        checks whether the new parent FR is in the same tree
        cannot change tree! (treeID)
    '''
    theFR = db.query(models.FunctionalRequirement).filter(models.FunctionalRequirement.id == FRid).first()
    theFR.name = FRdata.name
    theFR.description = FRdata.description

    # check if we need to change parent, too:
    if FRdata.rfID != theFR.rfID:
        theNewParent = db.query(models.DesignSolution).filter(models.DesignSolution.id == FRdata.rfID).first()

        # check if we are in the same tree
        if theNewParent.tree == theFR.tree:
            theFR.rfID = theNewParent.id
        else:
            raise EfmElementNotInTreeException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit FR; new parent DS is in another tree"
            )
    db.commit()
    return theFR
    
### DS
def get_DS_with_tree(db:Session, DSid: int):
    ''' 
        returns a DS object with all details
    '''
    try:
        theDS = db.query(models.DesignSolution).options(eagerload('requires_functions')).filter(models.DesignSolution.id == DSid).first()
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

def get_DS_info(db:Session, DSid: int):
    ''' 
        returns a DS object with all details
        PROBLEM CASE NOT WORKING RIGHT NOW
    '''
    #try:
    theDS = db.query(models.DesignSolution).options(lazyload('requires_functions')).filter(models.DesignSolution.id == DSid).first()
    if theDS:
        print(theDS.__dict__)
        theDSinfo = schemas.DSinfo.construct(theDS.__dict__)
        return theDSinfo
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DS with ID {} does not exist.".format(DSid)
        )
    # except EfmElementNotFoundException:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="DS with ID {} does not exist.".format(DSid)
    #     )
    # except TypeError:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="DSid needs to be an integer"
    #     )

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

    # check for tree similarity
    if theParent.treeID != newDS.treeID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create new DS; parent FR is in another tree! (DS parent ID: {}, FR parent ID: {}".format(newDS.treeID, theParent.treeID)
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
        checks whether the new parent FR is in the same tree
        cannot change tree! (treeID)
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

        # check if we are in the same tree
        if theNewParent.tree == theDS.tree:
            theDS.isbID = theNewParent.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit DS; new parent FR is in another tree"
            )
    db.commit()
    return theDS
 
### DP todo!! 
def get_DP(db:Session, DPid: int):
    return not_yet_implemented()
    
def create_DP(db: Session, parentID: int, newDP: schemas.DPnew):
    return not_yet_implemented()

def delete_DP(db:Session, DPid: int):
    return not_yet_implemented()

def edit_DP(db: Session, DPid: int, DPdata: schemas.DPnew):
    return not_yet_implemented()

### DP todo!! 
def get_IW(db:Session, IWid: int):
    return not_yet_implemented()

def create_IW(db: Session,  newIW: schemas.IWnew):
    return not_yet_implemented()

def delete_IW(db:Session, IWid: int):
    return not_yet_implemented()

def edit_IW(db: Session, IWid: int, IWdata: schemas.IWnew):
    return not_yet_implemented()

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
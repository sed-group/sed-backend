from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session, lazyload, eagerload
from typing import List
from enum import Enum
from sqlalchemy import inspect

from apps.EFMbackend.exceptions import EfmElementNotFoundException
import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas


# EFM database setup
## EXPERIMENTARY
try:
    from apps.EFMbackend.database import engine as efmEngine
    from apps.EFMbackend.models import Base as efmBase
    efmBase.metadata.create_all(bind=efmEngine)
    print(" EFM databases created")
except:
    print(" /!\\ could not create EFM databases")

# information dict for multi-type fetch/post functions
objTypes = {
    'DS': {
        'model': models.DesignSolution,
        'schema': schemas.DesignSolution,
        'str': 'Design Solution'
    },
    'FR': {
        'model': models.FunctionalRequirement,
        'schema': schemas.FunctionalRequirement,
        'str': 'Functional Requirement'
    },
    'tree': {
        'model': models.Tree,
        'schema': schemas.Tree,
        'str': 'EF-M tree'
    },
    'concept': {
        'model': models.Concept,
        'schema': schemas.Concept,
        'str': 'EF-M concept'
    },
    'iw': {
        'model': models.InteractsWith,
        'schema': schemas.InteractsWith,
        'str': 'interacts with'
    },
    
}

class efmObj(str, Enum):
    DS = 'DS'
    FR = 'FR'
    TREE = 'tree'
    CONCEPT = 'concept'

### general GET, POST, DELETE and PUT
def get_EFMobject(db: Session, objType: efmObj, objID: int):
    '''
        fetches an EF-M object via its id from the database
        what kind of object is defined via type
        returns schemas.object or raises exception
    '''

    objData = objTypes[objType]

    try:
        theObjOrm = db.query(objData['model']).filter(objData['model'].id == objID).first()
        if theObjOrm:
            theObjPydantic = objData['schema'].from_orm(theObjOrm)
            return theObjPydantic
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{} with ID {} does not exist.".format(objData['str'], objID)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{} with ID {} does not exist.".format(objData['str'], objID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="objID needs to be an integer"
        )

def get_EFMobjectAll(db: Session, objType: efmObj, treeID:int=0, limit: int = 100, offset:int = 0, ):
    '''
        fetches a list of EF-M objects of one type
        from offset to limit; if limit=0 returns all
        if treeID is given, limited to objects related to that one tree
        returns List[schemas.object] or raises exception
    '''

    objData = objTypes[objType]

    try:
        if treeID:
            theObjOrmList = db.query(objData['model']).filter(objData['model'].treeID == treeID)
        else:
            theObjOrmList = db.query(objData['model'])

        if limit:
            theObjOrmList = theObjOrmList.offset(offset).limit(limit)
        else:
            theObjOrmList = theObjOrmList.all()
        
        # rewrite to schema:
        theObjPydanticList = []

        for o in theObjOrmList:
            theObjPydantic = objData['schema'].from_orm(o)
            theObjPydanticList.append(theObjPydantic)

        return theObjPydanticList
    
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not load {}".format(objData['str'])
        )

    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type exception when trying to fetch {}".format(objData['str'])
        )

def new_EFMobject(db: Session, objType: efmObj, objData):
    '''
    stores objData as a new object depending on objType in the database
    returns a schemas.objType
    ## TODO:
    validation of object data to objInfo['schema']
    ##
    '''

    objInfo = objTypes[objType]

    try: 
        theObjOrm = objInfo['model'](**objData.dict())
        db.add(theObjOrm)
        db.commit()

        theObjPydantic = objInfo['schema'].from_orm(theObjOrm)
        return theObjPydantic
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database did not accept new {}.".format(objInfo['str'])
        )

def delete_EFMobject(db: Session, objType: efmObj, objID: int):
    '''
    deletes an object by ID
    '''

    objInfo = objTypes[objType]

    try:
        db.query(objInfo['model']).filter(objInfo['model'].id == objID).delete()
        db.commit()
        return True
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="objID needs to be an integer"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database could not delete {}.".format(objInfo['str'])
        )

def edit_EFMobject(db: Session, objType: efmObj, objID: int, objData):
    '''
    edits an object by ID and objData
    ## TODO:
    validation of object data to objInfo['schema']
    ##
    '''

    objInfo = objTypes[objType]

    # try: 
    theObjOrm = db.query(objInfo['model']).filter(objInfo['model'].id == objID).first()
    
    # writing all the info we want to write:
    for key, value in objData.dict().items():
        print(key, value)
        # theObjOrm.__dict__[key] = value
        # print(theObjOrm.__dict__[key])
        setattr(theObjOrm, key, value)

    print(theObjOrm)

    # # write values
    # theDPorm.name = DPdata.name
    # theDPorm.value = DPdata.value
    # theDPorm.unit = DPdata.unit
    # theDPorm.dsID = DPdata.dsID
    # theDPorm.treeID = DPdata.treeID

    # and write back to DB
    db.commit()

    print(theObjOrm)

    # convert to pydantic
    theObjPydantic = objInfo['schema'].from_orm(theObjOrm)
    return theObjPydantic
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Database could not edit {} with ID {}".format(objInfo['str'], objID)
    #     )

## Specialiced DB Functions
def tree_set_topLvlDs(db: Session, treeID: int, dsID: int):
    ''' 
    sets the topLvlDS of an existing tree
    needed in initial creation of a tree 
    '''
    try:
        theTree = db.query(models.Tree).options(lazyload('topLvlDS')).filter(models.Tree.id == treeID).first()
        theTree.topLvlDSid = dsID

        db.commit()
        pydanticTree = schemas.Tree.from_orm(theTree)
        return pydanticTree
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type error when setting topLvlDSid for tree id:{}".format(treeID)
        )

def get_treeInfoList(db: Session) -> List[schemas.TreeInfo]:
    # fetches all tree items and converts to treeInfo list
    
    ormTreeList = db.query(models.Tree)
    returnList = []
    for t in ormTreeList:
        treeInfo = schemas.TreeInfo(t)
        returnList.append(treeInfo)
    return returnList
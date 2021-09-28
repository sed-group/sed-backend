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
efm_object_types = {
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

class EfmObjectTypes(str, Enum):
    DS = 'DS'
    FR = 'FR'
    TREE = 'tree'
    CONCEPT = 'concept'

### general GET, POST, DELETE and PUT
def get_EFMobject(db: Session, efm_object_type: EfmObjectTypes, objID: int):
    '''
        fetches an EF-M object via its id from the database
        what kind of object is defined via type
        returns schemas.object or raises exception
    '''

    object_data = efm_object_types[efm_object_type]

    try:
        the_object_for_orm = db.query(object_data['model']).filter(object_data['model'].id == objID).first()
        if the_object_for_orm:
            the_object_as_pydantic_model = object_data['schema'].from_orm(the_object_for_orm)
            return the_object_as_pydantic_model
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="{} with ID {} does not exist.".format(object_data['str'], objID)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{} with ID {} does not exist.".format(object_data['str'], objID)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="objID needs to be an integer"
        )

def get_EFMobjectAll(db: Session, efm_object_type: EfmObjectTypes, tree_id:int=0, limit: int = 100, offset:int = 0, ):
    '''
        fetches a list of EF-M objects of one type
        from offset to limit; if limit=0 returns all
        if tree_id is given, limited to objects related to that one tree
        returns List[schemas.object] or raises exception
    '''

    object_data = efm_object_types[efm_object_type]

    try:
        if tree_id:
            the_object_for_ormList = db.query(object_data['model']).filter(object_data['model'].tree_id == tree_id)
        else:
            the_object_for_ormList = db.query(object_data['model'])

        if limit:
            the_object_for_ormList = the_object_for_ormList.offset(offset).limit(limit)
        else:
            the_object_for_ormList = the_object_for_ormList.all()
        
        # rewrite to schema:
        the_object_as_pydantic_modelList = []

        for o in the_object_for_ormList:
            the_object_as_pydantic_model = object_data['schema'].from_orm(o)
            the_object_as_pydantic_modelList.append(the_object_as_pydantic_model)

        return the_object_as_pydantic_modelList
    
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not load {}".format(object_data['str'])
        )

    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type exception when trying to fetch {}".format(object_data['str'])
        )

def new_efm_object(db: Session, efm_object_type: EfmObjectTypes, object_data):
    '''
    stores object_data as a new object depending on efm_object_type in the database
    returns a schemas.efm_object_type
    ## TODO:
    validation of object data to object_type_info['schema']
    ##
    '''

    object_type_info = efm_object_types[efm_object_type]

    # try: 
    the_object_for_orm = object_type_info['model'](**object_data.dict())
    db.add(the_object_for_orm)
    db.commit()

    the_object_as_pydantic_model = object_type_info['schema'].from_orm(the_object_for_orm)
    return the_object_as_pydantic_model
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Database did not accept new {}.".format(object_type_info['str'])
    #     )

def delete_EFMobject(db: Session, efm_object_type: EfmObjectTypes, objID: int):
    '''
    deletes an object by ID
    '''

    object_type_info = efm_object_types[efm_object_type]

    try:
        db.query(object_type_info['model']).filter(object_type_info['model'].id == objID).delete()
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
            detail="Database could not delete {}.".format(object_type_info['str'])
        )

def edit_EFMobject(db: Session, efm_object_type: EfmObjectTypes, objID: int, object_data):
    '''
    edits an object by ID and object_data
    ## TODO:
    validation of object data to object_type_info['schema']
    ##
    '''

    object_type_info = efm_object_types[efm_object_type]

    # try: 
    the_object_for_orm = db.query(object_type_info['model']).filter(object_type_info['model'].id == objID).first()
    
    # writing all the info we want to write:
    for key, value in object_data.dict().items():
        print(key, value)
        # the_object_for_orm.__dict__[key] = value
        # print(the_object_for_orm.__dict__[key])
        setattr(the_object_for_orm, key, value)

    print(the_object_for_orm)

    # # write values
    # theDPorm.name = DPdata.name
    # theDPorm.value = DPdata.value
    # theDPorm.unit = DPdata.unit
    # theDPorm.dsID = DPdata.dsID
    # theDPorm.tree_id = DPdata.tree_id

    # and write back to DB
    db.commit()

    print(the_object_for_orm)

    # convert to pydantic
    the_object_as_pydantic_model = object_type_info['schema'].from_orm(the_object_for_orm)
    return the_object_as_pydantic_model
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Database could not edit {} with ID {}".format(object_type_info['str'], objID)
    #     )

## Specialiced DB Functions
def tree_set_top_lvl_ds(db: Session, tree_id: int, dsID: int):
    ''' 
    sets the top_lvl_ds of an existing tree
    needed in initial creation of a tree 
    '''
    try:
        the_tree = db.query(models.Tree).options(lazyload('top_level_ds')).filter(models.Tree.id == tree_id).first()
        the_tree.top_level_ds_id = dsID

        db.commit()
        pydantic_tree = schemas.Tree.from_orm(the_tree)
        return pydantic_tree
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type error when setting top level DS id for tree id:{}".format(tree_id)
        )

def tree_set_subproject(db: Session, tree_id: int, new_subproject_id: int) -> schemas.Tree:
    ''' 
    sets the subproject id of an existing tree
    needed in initial creation of a tree 
    '''
    try:
        the_tree = db.query(models.Tree).filter(models.Tree.id == tree_id).first()
        the_tree.subproject_id = new_subproject_id

        db.commit()
        pydantic_tree = schemas.Tree.from_orm(the_tree)
        return pydantic_tree
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type error when setting top_lvl_dsid for tree id:{}".format(tree_id)
        )



def get_tree_info_list(db: Session) -> List[schemas.TreeInfo]:
    # fetches all tree items and converts to treeInfo list
    
    ormTreeList = db.query(models.Tree)
    returnList = []
    for t in ormTreeList:
        treeInfo = schemas.TreeInfo(t)
        returnList.append(treeInfo)
    return returnList
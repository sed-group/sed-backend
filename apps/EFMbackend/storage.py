from fastapi import HTTPException, Depends, status
from typing import List
from enum import Enum
import weakref
from mysql.connector.pooling import PooledMySQLConnection

from apps.EFMbackend.exceptions import EfmElementNotFoundException
# import apps.EFMbackend.models as models
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

# information object for multi-type fetch/post functions
class EFM_OBJECT_TYPES():
    # class which provides object information for the "get_all" and "get_one" function
    # use EFM_OBJECT_TYPESs.get_by_name('name')
    _instances = set()
    def __init__(self, name:str, table_name: str, schema_in, schema_out, schema_edit=None, to_string: str = ''):
        self.name = name
        self.schema_in = schema_in
        self.schema_out = schema_out
        if schema_edit:
            self.schemEdit = schema_edit
        else: 
            self.schema_edit = schema_in

        if to_string == '':
            self.to_string = self.name
        else:
            self.to_string = to_string
        self.table_name = table_name
        self._instances.add(weakref.ref(self))

    @classmethod
    def getinstances(cls):
        dead = set()
        for ref in cls._instances:
            obj = ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -= dead

    @classmethod
    def get_by_name(cls, name:str):
        for obj in cls.getinstances():
            if obj.name == name:
                return obj

DESIGNSOLUTION = EFM_OBJECT_TYPES(
    name = 'DS', 
    table_name = 'efm_designsolution', 
    schema_in = schemas.DSnew, 
    schema_out = schemas.DesignSolution,
    schema_edit = schemas.DSnew,
    to_string = 'Design Solution'
    )
FUNCTIONALREQUIREMENT = EFM_OBJECT_TYPES(
    name = 'FR', 
    table_name = 'efm_functionalrequirement', 
    schema_in = schemas.FRnew, 
    schema_out = schemas.FunctionalRequirement,
    schema_edit = schemas.FRnew,
    to_string = 'Functional Requirement'
    )

TREE = EFM_OBJECT_TYPES(
    name = 'tree', 
    table_name = 'efm_trees', 
    schema_in = schemas.TreeNew, 
    schema_out = schemas.TreeInfo,
    schema_edit = schemas.TreeNew,
    to_string = 'EFM Tree'
    )

INTERACTSWITH = EFM_OBJECT_TYPES(
    name = 'iw', 
    table_name = 'efm_interactswith', 
    schema_in = schemas.IWnew, 
    schema_out = schemas.InteractsWith,
    schema_edit = schemas.IWnew,
    to_string = 'Interacts With'
    )
    
CONSTRAINT = EFM_OBJECT_TYPES(
    name = 'c', 
    table_name = 'efm_constraints', 
    schema_in = schemas.ConstraintNew, 
    schema_out = schemas.Constraint,
    schema_edit = schemas.ConstraintNew,
    to_string = 'Constraint'
    )

CONCEPT = EFM_OBJECT_TYPES(
    name = 'concept', 
    table_name = 'efm_concepts', 
    schema_in = schemas.ConceptNew, 
    schema_out = schemas.Concept,
    schema_edit = schemas.ConceptEdit,
    to_string = 'Design Concept'
    )

class EfmObjectTypes(str, Enum):
    DS = 'DS'
    FR = 'FR'
    TREE = 'tree'
    CONSTRAINT = 'c'
    CONCEPT = 'concept'

### general GET, POST, DELETE and PUT
def get_efm_object(db: PooledMySQLConnection, efm_object_type: EfmObjectTypes, object_id: int):
    '''
        fetches an EF-M object via its id from the database
        what kind of object is defined via type
        returns schemas.object or raises exception
    '''

    object_data = EFM_OBJECT_TYPES.get_by_name(efm_object_type)

    # try:
    sql_select_Query =\
        f'SELECT * FROM {object_data.table_name} ' + \
        f'WHERE id = {object_id}'
    print(sql_select_Query)
    cursor = db.cursor()
    cursor.execute(sql_select_Query)
    # get the record
    db_response = cursor.fetchone()

    if not db_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{object_data.to_string} with ID {object_id} does not exist."
        )

    # convert to dictionary:
    db_response = dict(zip(cursor.column_names, db_response))

    response_object = object_data.schema_out(**db_response)
    
    return response_object

    # except EfmElementNotFoundException:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"{object_data.to_string} with ID {object_id} does not exist."
    #     )
    # except TypeError:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="object_id needs to be an integer"
    #     )

def get_efm_objects_all_of_tree(
    db: PooledMySQLConnection,
    efm_object_type: EfmObjectTypes,
    tree_id:int=0,
    limit: int = 100,
    offset:int = 0,
    ):
    '''
        fetches a list of EF-M objects of one type
        from offset to limit; if limit=0 returns all
        if tree_id is given, limited to objects related to that one tree
        returns List[schemas.object] or raises exception
    '''

    object_data = EFM_OBJECT_TYPES.get_by_name(efm_object_type)

    try:

        sql_select_Query = "SELECT * " + \
            f"FROM {object_data.table_name} "

        if tree_id:
            sql_select_Query = sql_select_Query + \
                f"WHERE tree_id = {tree_id} "

        if limit:
            sql_select_Query = sql_select_Query + \
                f"LIMIT {limit} " + \
                f"OFFSET {offset} "
        
        sql_select_Query = sql_select_Query + ';'

        cursor = db.cursor()
        cursor.execute(sql_select_Query)

        db_response = cursor.fetchall()

        # converting database result to dict
        dict_array = []
        for row in db_response:
            dict_array.append(dict(zip(cursor.column_names, row)))
        db_response = dict_array
        
        # rewrite to schema:
        the_object_as_pydantic_model_list = []

        for db_row in db_response:
            the_object_as_pydantic_model = object_data.schema_out(db_row)
            the_object_as_pydantic_model_list.append(the_object_as_pydantic_model)

        return the_object_as_pydantic_model_list

    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Type exception when trying to fetch {object_data.to_string}"
        )

def new_efm_object(
    db: PooledMySQLConnection,
    efm_object_type: EfmObjectTypes,
    object_data,
    commit: bool = True
    ):
    '''
    stores object_data as a new object depending on efm_object_type in the database
    returns a schemas.efm_object_type
    ##
    '''

    object_type_info = EFM_OBJECT_TYPES.get_by_name(efm_object_type)

    # checking input data
    try:
        object_pydantic = object_type_info.schema_in(**object_data.dict())
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Type exception when trying to write {object_type_info.to_string}"
        )
    # try:
    # building sql statement:
    sql_insert_query = f'INSERT INTO {object_type_info.table_name} '
    sql_col_names = []
    sql_values = []
    for key, val in object_pydantic.dict().items():
        sql_col_names.append(key)
        # check for string, then we need "'"
        if isinstance(val, str):
            sql_values.append(f"'{val}'")
        elif val == None:
            sql_values.append('NULL')
        else:
            sql_values.append(str(val))
    sql_insert_query = sql_insert_query + \
        f"({', '.join(sql_col_names)}) " + \
        f"VALUES ({', '.join(sql_values)})"
    
    print(sql_insert_query)

    cursor = db.cursor()
    cursor.execute(sql_insert_query)

    new_object_id = cursor.lastrowid

    if commit:
        db.commit()
        # fetching the object to return
        object_to_return = get_efm_object(
            db = db, 
            efm_object_type = efm_object_type, 
            object_id = new_object_id
            )
        return object_to_return
    else:
        return new_object_id
    # except:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail=f"Failed to enter new {object_type_info.to_string} into database."
    #     )

def delete_efm_object(
    db: PooledMySQLConnection,
    efm_object_type: EfmObjectTypes,
    object_id: int,
    commit: bool = True,
    ):
    '''
    deletes an object by ID
    '''

    object_type_info = EFM_OBJECT_TYPES.get_by_name(efm_object_type)

    try:
        sql_delete_query = "DELETE FROM " + \
            f"{object_type_info.table_name} WHERE id = {object_id}"

        cursor = db.cursor()
        cursor.execute(sql_delete_query)

        if commit:
            db.commit()
        return True

    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="object_id needs to be an integer"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Database could not delete {object_type_info.to_string}"
        )

def edit_efm_object(
    db: PooledMySQLConnection,
    efm_object_type: EfmObjectTypes, 
    object_id: int, 
    object_data,
    commit: bool = True,
    ):
    '''
    edits an object by ID and object_data
    '''
    print(f"efit_efm_object: type: {efm_object_type}; id: {object_id}; data: {object_data}")

    object_type_info = EFM_OBJECT_TYPES.get_by_name(efm_object_type)

    # checking input data
    try:
        object_pydantic = object_data.schema_in(object_data)
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Type exception when trying to write {object_type_info.to_string}"
        )

    try:
        sql_update_query = f"UPDATE {object_type_info.table_name} SET "

        for key, val in object_pydantic.dict().items():
            sql_update_string = sql_update_string + \
                f"{key} = {value} "

        sql_update_string = sql_update_string + \
            f"WHERE id = {object_id}"

        cursor = db.cursor()
        cursor.execute(sql_update_query)

        if commit:
            db.commit()
            # fetching the object to return
            object_to_return = get_efm_object(
                db = db, 
                efm_object_type = efm_object_type, 
                object_id = object_id
                )
            return object_to_return

        else:
            return object_id

    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not edit database entry for {} with ID {}".format(object_type_info.to_string, object_id)
        )


## Specialiced DB Functions
def tree_set_top_lvl_ds(db: PooledMySQLConnection, tree_id: int, ds_id: int):
    ''' 
    sets the top_lvl_ds of an existing tree
    needed in initial creation of a tree 
    '''
    object_type_info = EFM_OBJECT_TYPES.get_by_name('tree')
    try:
        sql_update_string = f"UPDATE {object_type_info.table_name} " + \
            f"SET top_level_ds_id = {ds_id} " + \
            f"WHERE id = {tree_id}"
        
        cursor = db.cursor()
        cursor.execute(sql_update_string)

        return tree_id

    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Type error when setting top level DS id for tree id:{}".format(tree_id)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to set top lvl DS id for tree {tree_id}"
        )


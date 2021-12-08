from fastapi import HTTPException, status
from typing import List
import json
import itertools #for permutations in concept DNA

from mysql.connector.pooling import PooledMySQLConnection

# efm modules import
# import apps.EFMbackend.models as models
import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.storage as storage
import apps.EFMbackend.algorithms as algorithms

from apps.EFMbackend.exceptions import *
from apps.EFMbackend.utils import not_yet_implemented

# imports from EF-M sub-modules
# from apps.EFMbackend.parameters.schemas import DesignParameter
# from apps.EFMbackend.parameters.storage import get_DP_all

# imports from core
from apps.core.db import get_connection
import apps.core.projects.storage as proj_storage
import apps.core.projects.models as proj_models

EFM_APP_SID = 'MOD.EFM'

#### TREES
def get_tree_list_of_user(db: PooledMySQLConnection, user_id: int, limit:int = 100, offset:int = 0) \
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
    subproject_list = proj_storage.db_get_user_subprojects_with_application_sid(db, user_id, EFM_APP_SID)

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

def create_tree(db: PooledMySQLConnection, project_id:int, new_tree: schemas.TreeNew, user_id: int):
    '''
        creates one new tree based on schemas.treeNew
        creates a new subproject in project_id 
        creates a top-level DS and associates its ID to tree.top_level_ds_id
    '''
    # first check whether project exists
    try:
        proj_storage.db_get_project_exists(db, project_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No project with ID {project_id} could be found"
        )

    # create tree without DS:
    the_tree_id = storage.new_efm_object(
        db = db,
        efm_object_type='tree',
        object_data= new_tree, 
        commit=False
        )

    # manufacture a top-levelDS:
    top_ds = schemas.DSnew(
        name=new_tree.name, 
        description="Top-level DS", 
        tree_id = the_tree_id, 
        is_top_level_ds = True,
        )

    # creating the DS in the DB
    top_ds_id = storage.new_efm_object(
        db = db,
        efm_object_type='DS',
        object_data= top_ds,
        commit=False
        )

    # setting the tree topLvlDS
    storage.tree_set_top_lvl_ds(
        db= db,
        tree_id = the_tree_id,
        ds_id= top_ds_id,
        )

    # create new sub-project on core level:
    new_subproject_data = proj_models.SubProjectPost(
        application_sid = EFM_APP_SID,
        native_project_id = the_tree_id,
    )
    
    new_subproject = proj_storage.db_post_subproject(
        connection = db, 
        subproject = new_subproject_data,
        current_user_id = user_id,
        project_id = project_id
        )
    
    db.commit()

    # fetch tree to return
    the_tree = storage.get_efm_object(
        db = db,
        efm_object_type = 'tree',
        object_id = the_tree_id,
        )

    return the_tree

def edit_tree(db: PooledMySQLConnection, tree_id: int, tree_data: schemas.TreeNew):
    return storage.edit_efm_object(
        db = db, 
        efm_object_type='tree',
        object_id= tree_id,
        object_data= tree_data
        )

def get_tree_details(db: PooledMySQLConnection, tree_id: int):
    ''' 
        returns a tree object with all details
        returns a schemas.Tree
    '''
    the_tree = storage.get_efm_object(db, 'tree', tree_id)
    return the_tree

def delete_tree(db: PooledMySQLConnection, tree_id: int):
    '''
        deletes tree based on id 
        also deletes the related subproject in core
    '''
    
    return_value = storage.delete_efm_object(
        db = db,
        efm_object_type = 'tree',
        object_id = tree_id
        )
    # print(return_value)
    # deleting the respective sub-project:
    # try:
    #     subproject = proj_storage.db_get_subproject_native(
    #         connection = db, 
    #         application_sid = EFM_APP_SID,
    #         native_project_id = tree_id
    #         )
    #     proj_storage.db_delete_subproject(
    #         connection = db,
    #         project_id = subproject.project_id,
    #         subproject_id = subproject.id,
    #         )
    # except:
    #     return_value = False
    db.commit()

    return return_value

def get_tree_data(db: PooledMySQLConnection, tree_id: int, depth:int=0):
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
    # for ds in all_ds:
    #     pydantic_ds_tree = schemas.DesignSolution.from_orm(ds)
    #     the_ds_info = schemas.DesignSolution(**pydantic_ds_tree.dict())
    #     the_ds_info.update(pydantic_ds_tree)
    #     tree_data.ds.append(the_ds_info)
    tree_data.ds = all_ds

    # fetch FR
    all_fr = storage.get_efm_objects_all_of_tree(db, 'FR', tree_id, depth)
    # for fr in all_fr:
    #     pydantic_fr_tree = schemas.FunctionalRequirement.from_orm(fr)
    #     the_fr_info = schemas.FunctionalRequirement(**pydantic_fr_tree.dict())
    #     the_fr_info.update(pydantic_fr_tree)
    #     tree_data.fr.append(the_fr_info)
    tree_data.fr = all_fr

    # fetch iw
    all_iw = storage.get_efm_objects_all_of_tree(db, 'iw', tree_id, depth)
    tree_data.iw = all_iw

    # fetch DP
    # all_dp = get_DP_all(db, tree_id, depth)
    # tree_data.dp = all_dp

    # fetch constraints
    all_c = storage.get_efm_objects_all_of_tree(db, 'c', tree_id, depth)
    tree_data.c = all_c

    return tree_data

def create_tree_from_json(db: PooledMySQLConnection, project_id:int, tree_data: schemas.TreeData, user_id: int ):
    '''
        creates an entirely new tree based on the provided json data
    '''
    # first create tree
    tree_new = schemas.TreeNew(**tree_info.dict())

    the_tree = create_tree(
        db = db,
        project_id = project_id,
        new_tree = tree_new,
        user_id = user_id
        )

    # an array to collect if something goes wrong:
    tree_creation_errors = []

    '''
    naming convention:
        input_ to hold the data from the original json
        _data converted for input format
        created_ to hold the newly created object as in DB
    '''
    # edit top-lvl-ds
    input_top_lvl_ds = next((ds for ds in tree_data.ds if ds.is_top_level_ds), None)
    top_lvl_ds_data = schemas.DSnew(**input_top_lvl_ds.dict())
    
    # dict to match the input ids with databas ids
    # {originalID: databasID}
    id_matching_list = {}

    created_top_lvl_ds = edit_DS(
        db = db,
        ds_id = the_tree.top_level_ds_id,
        ds_data = top_lvl_ds_data
        )
    
    # push into id list
    id_matching_list[input_top_lvl_ds.id] = create_top_lvl_ds.id

    id_matching_list = create_tree_recursively(
        db = db,
        efm_element_list = tree_data,
        ds_from_list = input_top_lvl_ds,
        ds_from_db = created_top_lvl_ds,
        id_list = id_matching_list
        )
    
    # creating CONSTRAINTS
    for input_c in tree_data.c:
        data_c = schemas.ConstraintNew(**input_c.dict())

        # substitute icb_id 
        data_c.icb_id = id_matching_list[input_c.icb_id]

        created_c = create_constraint(db = db, c_new = data_c)
    
    # creating IW
    for input_iw in tree_data.iw:
        data_iw = schemas.IWnew(**input_iw.dict())

        # substitute ids
        data_iw.from_ds_id = id_matching_list[input_iw.from_ds_id]
        data_iw.to_ds_id = id_matching_list[input_iw.to_ds_id]

        created_iw = create_IW(db=db, iw_new=data_iw)
    
def create_tree_recursively(
    db: PooledMySQLConnection,
    efm_element_list: schemas.TreeData,
    ds_from_list: schemas.DesignSolution,
    ds_from_db: schemas.DesignSolution,
    id_list: dict
    ):
    '''
        iterates through efm_element_list and creates all DS and FR recursively
        returns efm_element_list with all used DS and FR removed
    '''

    # filtering for the children FR of DS
    input_fr_list = [fr for fr in efm_element_list.fr if fr.isb_id == ds_from_list.id]

    for input_fr in input_fr_list:
        data_fr = schemas.FRnew(**input_fr.dict())
        data_fr.rf_id = ds_from_db.id
        
        created_fr = create_FR(data_fr)

        if created_fr:
            id_list[input_fr.id] = created_fr.id

            # now the subsequent DS:
            # filtering for children
            input_ds_list = [ds for ds in efm_element_list.ds if ds.rf_id == input_fr.id]
             
            for input_ds in input_ds_list:
                data_ds = schemas.DSnew(**input_ds.dict())
                data_ds.rf_id = created_fr.id

                created_ds = create_DS(db=db, new_ds = data_ds)
                
                if created_ds:
                    efm_element_list.ds.remove(input_ds)
                    id_list[input_ds.id] = created_ds.id

                    # recursive call for child elements:
                    left_over_elements = create_tree_recursively(
                        db = db,
                        efm_element_list = efm_element_list,
                        ds_from_list = input_ds, ds_from_db = created_ds,
                        id_list = id_list,
                        )

    return left_over_elements

### CONCEPTS
def get_all_concepts(db: PooledMySQLConnection, tree_id: int, limit:int=100, offset: int = 0):
    '''
    returns a list of all concepts of the tree identified via tree_id
    '''
    return storage.get_efm_objects_all_of_tree(db, 'concept', tree_id, limit, offset)

def get_concept(db: PooledMySQLConnection, cID: int):
    return storage.get_efm_object(db, 'concept', cID)

def edit_concept(db: PooledMySQLConnection, cID: int, cData: schemas.ConceptEdit):
    return storage.edit_efm_object(db, 'concept', cID, cData)

### FR
def get_FR_info(db: PooledMySQLConnection, fr_id: int):
    ''' 
        returns a FR object with all details
        but instead of relationships only ids
    ''' 
    return storage.get_efm_object(db, 'FR', fr_id)

def create_FR(db: PooledMySQLConnection, fr_new: schemas.FRnew):
    '''
        creates new FR based on schemas.FRnew (name, description) 
        associates it to DS with parentID via FR.rf_id ("requires function")
    '''
    # checking if parent exists
    parent_ds = storage.get_efm_object(db, 'DS', fr_new.rf_id)
    # setting tree_id for fetching
    fr_new.tree_id = parent_ds.tree_id
    
    return storage.new_efm_object(db, 'FR', fr_new)
    
def delete_FR(db: PooledMySQLConnection, fr_id: int):
    '''
        deletes FR based on id 
    '''
    return storage.delete_efm_object(db, 'FR', fr_id)

def edit_FR(db: PooledMySQLConnection, fr_id: int, fr_data: schemas.FRnew):
    '''
        overwrites the data in the FR identified with fr_id with the data from fr_data
        can change parent (i.e. isb), name and description
        tree_id is set through parent; therefore, change of tree is theoretically possible
    '''
    # first we need to set the tree_id, fetched from the parent DS
    parent_ds = storage.get_efm_object(db, 'DS', fr_data.rf_id)
    fr_data.tree_id = parent_ds.tree_id

    return storage.edit_efm_object(db, 'FR', fr_id, fr_data)
    
def new_parent_FR(db: PooledMySQLConnection, fr_id: int, ds_id: int):
    '''
    sets ds_id as new rf_id for FR
    i.e. a change in parent
    '''
    # fetch the FR data
    fr_data = storage.get_efm_object(db, 'FR', fr_id)
    # first we check if the new parent exists
    new_parent_DS = storage.get_efm_object(db, 'DS', ds_id)
    
    # check for same tree
    same_tree(fr_data, new_parent_DS)
    # check whether new parent is eligible
    new_parent_loop_prevention(db, fr_data, new_parent_DS)

    # convert to FRnew object to avoid writing child relations
    fr_data = schemas.FRnew(**fr_data.dict())
    # set new parent ID
    fr_data.rf_id = new_parent_DS.id
    
    # store it
    return storage.edit_efm_object(db, 'FR', fr_id, fr_data)


### DS
def get_DS_info(db: PooledMySQLConnection, ds_id: int):
    ''' 
        returns a DS object with all details
        but instead of relationships only ids
    '''    
    return storage.get_efm_object(db, 'DS', ds_id)

def create_DS(db: PooledMySQLConnection, new_ds: schemas.DSnew):
    '''
        creates new DS based on schemas.DSnew (name, description) 
        associates it to 
    '''
    # first we need to set the tree_id, fetched from the parent FR
    parent_fr = storage.get_efm_object(db, 'FR', new_ds.isb_id)
    new_ds.tree_id = parent_fr.tree_id

    return storage.new_efm_object(db, 'DS', new_ds)
    
def delete_DS(db: PooledMySQLConnection, ds_id: int):
    '''
        deletes DS based on id 
    '''
    return storage.delete_efm_object(db, 'DS', ds_id)

def edit_DS(db: PooledMySQLConnection, ds_id: int, ds_data: schemas.DSnew):
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

def new_parent_DS(db: PooledMySQLConnection, ds_id: int, fr_id: int):
    '''
    sets fr_id as new isb_id for DS
    i.e. a change in parent
    '''
    # fetch the DS data
    ds_data = storage.get_efm_object(db, 'DS', ds_id)
    
    # first we check if the new parent exists
    new_parent_FR = storage.get_efm_object(db, 'FR', fr_id)
    # check for same tree
    same_tree(ds_data, new_parent_FR)
    # check whether new parent is eligible
    new_parent_loop_prevention(db, ds_data, new_parent_FR)

    # i.e. new_parent is not among children
    new_parent_loop_prevention(db, ds_data, new_parent_FR)

    # convert to DSnew object to avoid writing child relations
    ds_data = schemas.DSnew(**ds_data.dict())


    # set new parent ID
    ds_data.isb_id = new_parent_FR.id
    
    # store it
    return storage.edit_efm_object(db, 'DS', ds_id, ds_data)

### iw 
def get_IW(db: PooledMySQLConnection, iw_id: int):
    return storage.get_efm_object(db, 'iw', iw_id)

def create_IW(db: PooledMySQLConnection, iw_new: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        but don't have the same parent_fr
            --> this needs to check whether they are _on no level_ in alternative DS; so i'm afraid we need to iterate all the parent DS and check whether one of them are alternatives to each other?? 
            --> NOT IMPLEMENTED
        then commits to DB
    '''
    # getting parent elements for checks
    to_ds = storage.get_efm_object(db, 'DS', iw_new.to_ds_id)
    from_ds = storage.get_efm_object(db, 'DS', iw_new.from_ds_id)

    # checking if we're in the same tree:
    same_tree(to_ds, from_ds)
    # checking if iw are not related
    iw_not_related(db, from_ds, to_ds)

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

def delete_IW(db: PooledMySQLConnection, iw_id: int):
    return storage.delete_efm_object(db, 'iw', iw_id)

def edit_IW(db: PooledMySQLConnection, iw_id: int, iw_data: schemas.IWedit):
    '''
        first verifies whether the two DS are in the same tree, 
        then commits to DB
    '''
    # check if iw actually exists
    old_iw = storage.get_efm_object(
        db = db,
        efm_object_type = 'iw',
        object_id = iw_id
        )

    # check if we want to reset connections
    if not iw_data.to_ds_id:
        iw_data.to_ds_id = old_iw.to_ds_id
    if not iw_data.from_ds_id:
        iw_data.from_ds_id = old_iw.from_ds_id

    to_ds = storage.get_efm_object(db, 'DS', iw_data.to_ds_id)
    from_ds = storage.get_efm_object(db, 'DS', iw_data.from_ds_id)
    
    
    # checking if we're in the same tree:
    same_tree(to_ds, from_ds)
    # checking if parent DS are not related
    iw_not_related(db, from_ds, to_ds)

    iw_data.tree_id = to_ds.tree_id

    return storage.edit_efm_object(db, 'iw', iw_id, iw_data)

## constraints
def get_constraint(db: PooledMySQLConnection, c_id: int):
    return storage.get_efm_object(db, 'c', c_id)

def create_constraint(db: PooledMySQLConnection,  c_new: schemas.ConstraintNew):
    '''
        commits new constraint to DB
    '''
    icb_ds = storage.get_efm_object(db, 'DS', c_new.icb_id)

    # setting tree_id since its optional (backwards compatibility ^^)
    c_new.tree_id = icb_ds.tree_id

    return storage.new_efm_object(db, 'c', c_new)

def delete_constraint(db: PooledMySQLConnection, c_id = int):
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

def edit_constraint(db: PooledMySQLConnection, c_id: int, c_data: schemas.ConstraintNew):
    '''
        sets all values of constraint with c_id in db with data of c_data
        returns edited constraint
    '''
    # check if constraint exists
    constraint = storage.get_efm_object(
        db = db, 
        efm_object_type = 'c',
        object_id = c_id,
        )
    # overwrite tree_id for consistency
    c_data.tree_id = constraint.tree_id

    return storage.edit_efm_object(
        db = db,
        efm_object_type = 'c',
        object_id = c_id,
        object_data = c_data
        )

def new_parent_constraint(c_id: int, new_parent_id: int):
    ''' 
        sets the DS with new_parent_id as icb_id for the constraint with c_id
    '''
    with get_connection() as db:
    # check if constraint exists
        old_c = storage.get_efm_object(
            db = db, 
            efm_object_type = 'c', 
            object_id = c_id
        )
        # check if new parent exists
        new_parent_ds = storage.get_efm_object(
            db = db, 
            efm_object_type = 'ds', 
            object_id = new_parent_id
        )
        # check same tree
        if same_tree(old_c, new_parent_ds):
            new_c = schemas.ConstraintNew(**old_c.dict())
            new_c.icb_id = new_parent_ds.id

            # commit to DB
            return storage.edit_efm_object(
                db = db,
                efm_object_type = 'c', 
                object_id = c_id, 
                object_data = new_c
            )

## helper functions
async def run_instantiation(db: PooledMySQLConnection, tree_id: int):
    '''
    creates all instance concepts of a tree
    does not overwrite existing ones if they are included in the new instantiation
    '''    
    # fetch the old concepts, if available:
    all_old_concepts = storage.get_efm_objects_all_of_tree(db, 'concept', tree_id, 0) # will get deleted later
    all_new_concepts = []                           # will get added later

    the_tree = storage.get_efm_object(db, 'tree', tree_id)
    top_lvl_ds = storage.get_efm_object(db, 'DS', the_tree.top_level_ds_id)

    all_dna = alternative_configurations(db, top_lvl_ds)

    concept_counter = len(all_old_concepts) # for naming only - there might be better approaches to this

    for dna in all_dna:
        
        dna_string = str(dna) #json.dumps(dna)

        # check if concept with same DNA already exists, then jump:
        for old_concept in all_old_concepts:
            if old_concept.dna == dna:
                # remove from list so it won't get deleted:
                all_old_concepts.remove(old_concept)
                # add to list of all Concepts:
                all_new_concepts.append(old_concept)
                # and we don't need to create a new object for it, so we jump
                next()
        c_name = f"Concept {concept_counter}"
        c_data = {
            'name': c_name, 
            'dna': dna_string, 
            'tree_id': tree_id
        }
        new_concept = schemas.ConceptNew(**c_data)
        
        # add to DB:
        storage.new_efm_object(db, 'concept', new_concept)

        all_new_concepts.append(new_concept)
        concept_counter = concept_counter + 1

    # delete old concepts:
    for oC in all_old_concepts:
        storage.delete_efm_object(db, 'concept', oC.id)
        
    return all_new_concepts

def alternative_solutions(db: PooledMySQLConnection, the_fr: schemas.FunctionalRequirement):
    ## function for recursive generation of alternative concepts

    # returns a list of dicts with each DNA, including the_fr
    # each dna includes all DS IDs of an instance
    # compiles all DS' alternatives (adding all the DS dna to the all_dna list, and adding thisFR:respectiveDS on top.

    # all_dna collect's all the alternative's DNA, one alternative per entry in the list:
    all_dna = []

    # fethching child DS from DB
    is_solved_by = storage.get_efm_children(
        db = db,
        efm_object_type = 'FR',
        object_id = the_fr.id
        )

    for d in is_solved_by:
        # cerating the individual dna sequence for this FR:DS pair (but only their names):
        #print(d)
        this_dna = d.id
        # checking if there are any sub-configs for this DS, then we need to add the individual sequence to the end of EACH of the configuration's dna:
        if alternative_configurations(db, d):
            for ds_dna in alternative_configurations(d):
                # print("ds_dna: {}; this_dna: {}".format(ds_dna, this_dna))
                # add tp the respective sequence:
                ds_dna.append(this_dna)
                # print("ds_dna, combined: {}".format(ds_dna))
                # add the sequnce to the collectors:
                all_dna.append(ds_dna)
            # print('we append sth; all_dna: {}'.format(all_dna))
        else:
            # if we are at the bottom of the tree, i.e. the DS has no FR below it, it doesn't return an array.
            # so we need to make a new line DNA sequence!
            all_dna.append(this_dna)

    # returns the collector of all DNA:
    return all_dna

def alternative_configurations(db: PooledMySQLConnection, the_ds: schemas.DesignSolution):
    ## function for recursive generation of alternative concepts

    # creates the permutations of all child-FR alternative configurations
    # FR1 [dnaA, dnaB, dnaC]; FR2 [dna1, dna2]; FR3 [DNA]
    # --> [(dnaA, dna1, DNA), (dnaB, dna1, DNA), (dnaC, dna1, DNA),
    #      (dnaA, dna2, DNA), (dnaB, dna2, DNA), (dnaC, dna2, DNA)]
    all_dna = []
    all_configurations = []

    # fethching child DS from DB
    requires_functions = storage.get_efm_children(
        db = db,
        efm_object_type = 'DS',
        object_id = the_ds.id
        )

    for f in requires_functions:
        # creating a list of all DNA from each FR; one entry per FR
        # this will later be combinatorially multiplied (cross product)
        # f.linkToCC()
        new_dna = alternative_solutions(db, f)
        if len(new_dna):
            all_dna.append(new_dna)
        # print(" all_dna of {}: {}; fr:{}, altS: {}".format(self, all_dna, f, f.alternative_solutions()))

        # generating the combinatorial
        # the first "list" makes it put out a list instead of a map object
        # the map(list, ) makes it put out lists instead of tuples, needed for further progression on this...
            all_configurations = list(map(list, itertools.product(*all_dna)))

    # print(all_configurations)

    return all_configurations

def same_tree(obj_a, obj_b):
    '''
        checks wheter obj_a and obj_b have the same tree_id
        returns true if yes, raises error otherwise
    '''
    if (obj_a.tree_id == obj_b.tree_id):
        return True
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{obj_a.name} and {obj_b.name} need to be in the same tree"
        )

def all_parents(db, theObject, all_parents_list = []):
    '''
        object must be as from db
        returns a list of all parent objects of object
    '''
    # first we need to find the parent id
    # since we don't know the type of "object"
    new_parents_list = all_parents_list
    try:
        # case DS
        parent_id = theObject.isb_id
        parent_type = 'FR'
    except:
        try:
            #case FR
            parent_id = theObject.rf_id
            parent_type = 'DS'
        except:
            try:
                # case iw
                parent_id = theObject.from_ds_id
                parent_type = 'DS'
            except:
                try:
                    #case constraint
                    parent_id = theObject.icb_id
                    parent_type = 'DS'
                except:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Could not identify parent of object {theObject.type()}"
                    )

    if parent_id:
        new_parent = storage.get_efm_object(
            db = db, 
            efm_object_type = parent_type,
            object_id = parent_id
            )
        new_parents_list.append(new_parent)

        # recursive call
        new_parents_list = all_parents(
            db = db, 
            theObject = new_parent,
            all_parents_list= new_parents_list
            )
        return new_parents_list
    else:
        # case we reached the top of the tree
        return new_parents_list

def all_children(db, the_object, all_children_list = []):
    ''' 
        function only for DS and FR
        returns list of all DS and FR below in the tree
    '''
    
    new_children = storage.get_efm_children(
        db = db,
        efm_object_type = the_object.efm_type(),
        object_id = the_object.id
        )
    new_children_list = all_children_list
    new_children_list.extend(new_children)

    # recursive call
    for c in new_children:
        new_children_list.extend(all_children(
            db = db, 
            the_object = c, 
            all_children_list = new_children_list
            )
        )
    
    return new_children_list

def iw_not_related(db: PooledMySQLConnection, from_ds: schemas.DesignSolution, to_ds: schemas.DesignSolution):
    '''
        verifies that from_ds and to_ds are not in exclusively alternative concepts
        check is perfomred via having a different parent-DS with the same isb (same FR parent)
        returns true if not related,
        otherwise raises error
    '''
    from_parents = all_parents(db = db, theObject = from_ds)

    to_parents = all_parents(db = db, theObject = to_ds)

    # first search for FR where the two branches converge
    for fr_from_parent in from_parents:
        # check if it's an FR
        if fr_from_parent.efm_type() == 'FR':
            # check if it is shared among to and from parents
            if fr_from_parent in to_parents:
                # now, if to_parents and from_parents DO NOT share the same child of fr_parent, they are definite alternatives:

                # first we need to find the child DS of said DS in the from_parents
                fr_from_parent_child = next((ds for ds in from_parents if (ds.efm_type() == 'DS' and ds.isb_id == fr_from_parent.id)), None)

                # now we find the child DS of said shared FR in the to_parents list
                fr_to_parent_child = next((ds for ds in to_parents if (ds.efm_type() == 'DS' and ds.isb_id == fr_from_parent.id)), None)

                if fr_to_parent_child != fr_from_parent_child:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"{from_ds.name} is an exclusive alternative of {to_ds.name}, therefore they cannot share an iw! The respective (parent-) DS {fr_to_parent_child.name} and {fr_from_parent_child.name} are direct alternatives."
                    )
    
    return True

def new_parent_loop_prevention(db: PooledMySQLConnection, child, parent):
    '''
        verifies whether the parent is not among the children of child
        prevents loops when assigning new parents to DS or FR
        returns true or raises error
    '''

    grand_children = all_children(db = db, the_object = child)

    if parent in grand_children:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{parent.name} cannot be new parent of {child.name}, since it would create a loop! ({paret.name} is already a child of {child.name}.)"
        )
    else:
        return True
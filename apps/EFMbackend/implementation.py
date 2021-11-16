from fastapi import HTTPException, status
from typing import List
import json

from mysql.connector.pooling import PooledMySQLConnection

# efm modules import
# import apps.EFMbackend.models as models
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
from apps.core.db import get_connection
import apps.core.projects.storage as proj_storage
import apps.core.projects.models as proj_models

EFM_APP_SID = 'MOD.EFM'

#### TREES
def get_tree_list_of_user(user_id: int, limit:int = 100, offset:int = 0) \
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
    with get_connection() as db:
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

def create_tree(project_id:int, new_tree: schemas.TreeNew, user_id: int):
    '''
        creates one new tree based on schemas.treeNew
        creates a new subproject in project_id 
        creates a top-level DS and associates its ID to tree.top_level_ds_id
    '''
    with get_connection() as db:
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

def edit_tree(tree_id: int, tree_data: schemas.TreeNew):
    with get_connection() as db:
        return storage.edit_efm_object(db, 'tree', tree_id, tree_id)

def get_tree_details(tree_id: int):
    ''' 
        returns a tree object with all details
        returns a schemas.Tree
    '''
    with get_connection() as db:
        the_tree = storage.get_efm_object(db, 'tree', tree_id)
    return the_tree

def delete_tree(tree_id: int):
    '''
        deletes tree based on id 
        also deletes the related subproject in core
    '''
    
    with get_connection() as db:
        storage.delete_efm_object(
            db = db,
            efm_object_type = 'tree',
            object_id = tree_id
            )

    # deleting the respective sub-project:
        subproject = proj_storage.db_get_subproject_native(
            connection = db, 
            application_sid = EFM_APP_SID,
            native_project_id = tree_id
            )
        proj_storage.db_delete_subproject(
            connection = db,
            project_id = subproject.project_id,
            subproject_id = subproject.id,
            )
        db.commit()

        return True

def get_tree_data(tree_id: int, depth:int=0):
    '''
    returns a list of all obejcts related to a specific tree
    depth = 0 makes it return _all_ objects - can be quite big then!
    however, there is no sorting applied to the returned objects, so it is difficult to know which elements you get back...
    '''

    with get_connection() as db:
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

### CONCEPTS
def get_all_concepts(tree_id: int, limit:int=100, offset: int = 0):
    '''
    returns a list of all concepts of the tree identified via tree_id
    '''
    with get_connection() as db:
        return storage.get_efm_objects_all_of_tree(db, 'concept', tree_id, limit, offset)

def get_concept(cID: int):
    with get_connection() as db:
        return storage.get_efm_object(db, 'concept', cID)

def edit_concept(cID: int, cData: schemas.ConceptEdit):
    with get_connection() as db:
        return storage.edit_efm_object(db, 'concept', cID, cData)

### FR
def get_FR_info(fr_id: int):
    ''' 
        returns a FR object with all details
        but instead of relationships only ids
    ''' 
    with get_connection() as db:    
        return storage.get_efm_object(db, 'FR', fr_id)

def create_FR(fr_new: schemas.FRnew):
    '''
        creates new FR based on schemas.FRnew (name, description) 
        associates it to DS with parentID via FR.rf_id ("requires function")
    '''
    with get_connection() as db:
        # checking if parent exists
        parent_ds = storage.get_efm_object(db, 'DS', fr_new.rf_id)
        # setting tree_id for fetching
        fr_new.tree_id = parent_ds.tree_id
        
        return storage.new_efm_object(db, 'FR', fr_new)
    
def delete_FR(fr_id: int):
    '''
        deletes FR based on id 
    '''
    with get_connection() as db:
        return storage.delete_efm_object(db, 'FR', fr_id)

def edit_FR(fr_id: int, fr_data: schemas.FRnew):
    '''
        overwrites the data in the FR identified with fr_id with the data from fr_data
        can change parent (i.e. isb), name and description
        tree_id is set through parent; therefore, change of tree is theoretically possible
    '''
    with get_connection() as db:
        # first we need to set the tree_id, fetched from the parent DS
        parent_ds = storage.get_efm_object(db, 'DS', fr_data.rf_id)
        fr_data.tree_id = parent_ds.tree_id

        return storage.edit_efm_object(db, 'FR', fr_id, fr_data)
    
def new_parent_FR(fr_id: int, ds_id: int):
    '''
    sets ds_id as new rf_id for FR
    i.e. a change in parent
    '''
    with get_connection() as db:
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
def get_DS_info(ds_id: int):
    ''' 
        returns a DS object with all details
        but instead of relationships only ids
    '''    
    with get_connection() as db:
        return storage.get_efm_object(db, 'DS', ds_id)

def create_DS(new_ds: schemas.DSnew):
    '''
        creates new DS based on schemas.DSnew (name, description) 
        associates it to 
    '''
    with get_connection() as db:
        # first we need to set the tree_id, fetched from the parent FR
        parent_fr = storage.get_efm_object(db, 'FR', new_ds.isb_id)
        new_ds.tree_id = parent_fr.tree_id

        return storage.new_efm_object(db, 'DS', new_ds)
    
def delete_DS(ds_id: int):
    '''
        deletes DS based on id 
    '''
    with get_connection() as db:
        return storage.delete_efm_object(db, 'DS', ds_id)

def edit_DS(ds_id: int, ds_data: schemas.DSnew):
    '''
        overwrites the data in the DS identified with ds_id with the data from DSnew
        can change parent (i.e. isb), name and description
        checks whether the new parent FR is in the same tree
        cannot change tree! (tree_id)
    '''
    with get_connection() as db:
        # first we need to set (correct?) the tree_id, fetched from the parent FR
        parent_fr = storage.get_efm_object(db, 'FR', ds_data.isb_id)
        ds_data.tree_id = parent_fr.tree_id

        return storage.edit_efm_object(db, 'DS', ds_id, ds_data)

def new_parent_DS(ds_id: int, fr_id: int):
    '''
    sets fr_id as new isb_id for DS
    i.e. a change in parent
    '''
    with get_connection() as db:
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
def get_IW(iw_id: int):
    with get_connection() as db:
        return storage.get_efm_object(db, 'iw', iw_id)

def create_IW( iw_new: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        but don't have the same parent_fr
            --> this needs to check whether they are _on no level_ in alternative DS; so i'm afraid we need to iterate all the parent DS and check whether one of them are alternatives to each other?? 
            --> NOT IMPLEMENTED
        then commits to DB
    '''

    with get_connection() as db:
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

def delete_IW(iw_id: int):
    with get_connection() as db:
        return storage.delete_efm_object(db, 'iw', iw_id)

def edit_IW(iw_id: int, iw_data: schemas.IWnew):
    '''
        first verifies whether the two DS are in the same tree, 
        then commits to DB
    '''
    with get_connection() as db:
        to_ds = storage.get_efm_object(db, 'DS', iw_data.to_ds_id)
        from_ds = storage.get_efm_object(db, 'DS', iw_data.from_ds_id)
        
        # checking if we're in the same tree:
        same_tree(to_ds, from_ds)
        # checking if parent DS are not related
        iw_not_related(db, from_ds, to_ds)

        iw_data.tree_id = to_ds.tree_id

        return storage.edit_efm_object(db, 'iw', iw_id, iw_data)

## constraints
def get_constraint(c_id: int):
    with get_connection() as db:
        return storage.get_efm_object(db, 'c', c_id)

def create_constraint( c_new: schemas.ConstraintNew):
    '''
        commits new constraint to DB
    '''
    with get_connection() as db:

        icb_ds = storage.get_efm_object(db, 'DS', c_new.icb_id)

        # setting tree_id since its optional (backwards compatibility ^^)
        c_new.tree_id = icb_ds.tree_id

        return storage.new_efm_object(db, 'c', c_new)

def delete_constraint(c_id = int):
    '''
        deletes one constraint from db
        returns true or raises error
    '''
    with get_connection() as db:
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

def edit_constraint(c_id: int, c_data: schemas.ConstraintNew):
    '''
        sets all values of constraint with c_id in db with data of c_data
        returns edited constraint
    '''
    with get_connection() as db:
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
async def run_instantiation(tree_id: int):
    '''
    creates all instance concepts of a tree
    does not overwrite existing ones if they are included in the new instantiation
    '''    
    with get_connection() as db:
        # fetch the old concepts, if available:
        all_old_concepts = storage.get_efm_objects_all_of_tree(db, 'concept', tree_id, 0) # will get deleted later
        all_new_concepts = []                           # will get added later

        the_tree = storage.get_efm_object(db, 'tree', tree_id)

        all_dna = algorithms.alternative_configurations(the_tree.top_level_ds)

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
        efm_object_type = the_object.efmType(),
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
                fr_from_parent_child = next((ds for ds in from_parents if ds.isb_id == fr_from_parent.id), None)

                # now we find the child DS of said shared FR in the to_parents list
                fr_to_parent_child = next((ds for ds in to_parents if ds.isb_id == fr_from_parent.id), None)

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
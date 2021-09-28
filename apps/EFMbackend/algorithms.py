import itertools #for permutations in concept DNA
from sqlalchemy.orm import Session
from typing import List

import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.storage as storage

def alternative_solutions(the_fr: schemas.FunctionalRequirement):
    ## function for recursive generation of alternative concepts

    # returns a list of dicts with each DNA, including the_fr
    # each dna includes all DS IDs of an instance
    # compiles all DS' alternatives (adding all the DS dna to the all_dna list, and adding thisFR:respectiveDS on top.

    ################ BUG REPORT: ####################
    ## THis entire mechanism fails if there are FR without DS! Always have at least a dummy-DS!
    #################################################

    # all_dna collect's all the alternative's DNA, one alternative per entry in the list:
    all_dna = []

    for d in the_fr.is_solved_by:
        # cerating the individual dna sequence for this FR:DS pair (but only their names):
        #print(d)
        this_dna = d.id
        # checking if there are any sub-configs for this DS, then we need to add the individual sequence to the end of EACH of the configuration's dna:
        if alternative_configurations(d):
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

def alternative_configurations(the_ds: schemas.DesignSolution):
    ## function for recursive generation of alternative concepts

    # creates the permutations of all child-FR alternative configurations
    # FR1 [dnaA, dnaB, dnaC]; FR2 [dna1, dna2]; FR3 [DNA]
    # --> [(dnaA, dna1, DNA), (dnaB, dna1, DNA), (dnaC, dna1, DNA),
    #      (dnaA, dna2, DNA), (dnaB, dna2, DNA), (dnaC, dna2, DNA)]
    all_dna = []
    all_configurations = []
    for f in the_ds.requires_functions:
        # creating a list of all DNA from each FR; one entry per FR
        # this will later be combinatorially multiplied (cross product)
        # f.linkToCC()
        all_dna.append(alternative_solutions(f))
        # print(" all_dna of {}: {}; fr:{}, altS: {}".format(self, all_dna, f, f.alternative_solutions()))

        # generating the combinatorial
        # the first "list" makes it put out a list instead of a map object
        # the map(list, ) makes it put out lists instead of tuples, needed for further progression on this...
        all_configurations = list(map(list, itertools.product(*all_dna)))

    # print(all_configurations)

    return all_configurations


async def run_instantiation(db: Session, tree_id: int):
    '''
    creates all instance concepts of a tree
    does not overwrite existing ones if they are included in the new instantiation
    '''    
    # fetch the old concepts, if available:
    all_old_concepts = storage.get_EFMobjectAll(db, 'concept', tree_id, 0) # will get deleted later
    all_new_concepts = []                           # will get added later

    the_tree = storage.get_EFMobject(db, 'tree', tree_id)

    all_dna = alternative_configurations(the_tree.topLvlDS)

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

        new_concept = schemas.ConceptNew()
        new_concept.name = f"Concept {concept_counter}"
        new_concept.dna = dna_string
        new_concept.tree_id = tree_id
        
        # add to DB:
        storage.new_EFMobject(db, 'concept', new_concept)

        all_new_concepts.append(new_concept)
        concept_counter = concept_counter + 1

    # delete old concepts:
    for oC in all_old_concepts:
        storage.delete_EFMobject(db, 'concept', oC.id)
        
    return all_new_concepts

def prune_child_ds(ds: schemas.DesignSolution, dna: List[int]):
    '''
        takes a DS and removes all child DS _not_ in dna (dna to be a list of int)
    '''
    for fr in ds.requires_functions:
        for child_ds in fr.is_solved_by:
            # remove the DS not in DNA:
            if not child_ds.id in dna:
                fr.is_solved_by.remove(child_ds)
            else:
                # else prune the children, too
                child_ds = prune_child_ds(ds, dna)

    return ds

def allChildDS(fr: schemas.FunctionalRequirement, childList = []):
    '''
        iterates through all children of an FR and 
        returns a list of DS 
    '''
    new_child_list = childList

    for ds in fr.is_solved_by:
        new_child_list.append(ds)

        for fr in ds.requires_functions:
            new_child_list.extend(allChildDS(fr))

    return new_child_list

def allChildFR(ds: schemas.DesignSolution, childList = []):
    '''
        iterates through all children of a DS and 
        returns a list of FR
    '''
    new_child_list = childList

    for fr in ds.requires_functions:
        new_child_list.append(fr)
        
        for ds in fr.is_solved_by:
            new_child_list.extend(allChildFR(ds))

    return new_child_list


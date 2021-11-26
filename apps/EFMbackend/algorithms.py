from typing import List

import apps.EFMbackend.schemas as schemas

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


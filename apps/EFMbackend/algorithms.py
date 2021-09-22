import itertools #for permutations in concept DNA
from sqlalchemy.orm import Session
from typing import List

import apps.EFMbackend.schemas as schemas
import apps.EFMbackend.storage as storage

def alternativeSolutions(theFR: schemas.FunctionalRequirement):
    ## function for recursive generation of alternative concepts

    # returns a list of dicts with each DNA, including theFR
    # each dna includes all DS IDs of an instance
    # compiles all DS' alternatives (adding all the DS dna to the allDNA list, and adding thisFR:respectiveDS on top.

    ################ BUG REPORT: ####################
    ## THis entire mechanism fails if there are FR without DS! Always have at least a dummy-DS!
    #################################################

    # allDNA collect's all the alternative's DNA, one alternative per entry in the list:
    allDNA = []

    for d in theFR.is_solved_by:
        # cerating the individual dna sequence for this FR:DS pair (but only their names):
        #print(d)
        thisDNA = d.id
        # checking if there are any sub-configs for this DS, then we need to add the individual sequence to the end of EACH of the configuration's dna:
        if alternativeConfigurations(d):
            for dsDNA in alternativeConfigurations(d):
                # print("dsDNA: {}; thisDNA: {}".format(dsDNA, thisDNA))
                # add tp the respective sequence:
                dsDNA.append(thisDNA)
                # print("dsDNA, combined: {}".format(dsDNA))
                # add the sequnce to the collectors:
                allDNA.append(dsDNA)
            # print('we append sth; allDNA: {}'.format(allDNA))
        else:
            # if we are at the bottom of the tree, i.e. the DS has no FR below it, it doesn't return an array.
            # so we need to make a new line DNA sequence!
            allDNA.append(thisDNA)

    # returns the collector of all DNA:
    return allDNA

def alternativeConfigurations(theDS: schemas.DesignSolution):
    ## function for recursive generation of alternative concepts

    # creates the permutations of all child-FR alternative configurations
    # FR1 [dnaA, dnaB, dnaC]; FR2 [dna1, dna2]; FR3 [DNA]
    # --> [(dnaA, dna1, DNA), (dnaB, dna1, DNA), (dnaC, dna1, DNA),
    #      (dnaA, dna2, DNA), (dnaB, dna2, DNA), (dnaC, dna2, DNA)]
    allDNA = []
    allConfigurations = []
    for f in theDS.requires_functions:
        # creating a list of all DNA from each FR; one entry per FR
        # this will later be combinatorially multiplied (cross product)
        # f.linkToCC()
        allDNA.append(alternativeSolutions(f))
        # print(" allDNA of {}: {}; fr:{}, altS: {}".format(self, allDNA, f, f.alternativeSolutions()))

        # generating the combinatorial
        # the first "list" makes it put out a list instead of a map object
        # the map(list, ) makes it put out lists instead of tuples, needed for further progression on this...
        allConfigurations = list(map(list, itertools.product(*allDNA)))

    # print(allConfigurations)

    return allConfigurations


async def run_instantiation(db: Session, treeID: int):
    '''
    creates all instance concepts of a tree
    does not overwrite existing ones if they are included in the new instantiation
    '''    
    # fetch the old concepts, if available:
    allOldConcepts = storage.get_EFMobjectAll(db, 'concept', treeID, 0) # will get deleted later
    allNewConcepts = []                           # will get added later

    theTree = storage.get_EFMobject(db, 'tree', treeID)

    allDna = alternativeConfigurations(theTree.topLvlDS)

    conceptCounter = len(allOldConcepts) # for naming only - there might be better approaches to this

    for dna in allDna:
        
        dnaString = str(dna) #json.dumps(dna)

        # check if concept with same DNA already exists, then jump:
        for oldC in allOldConcepts:
            if oldC.dna == dna:
                # remove from list so it won't get deleted:
                allOldConcepts.remove(oldC)
                # add to list of all Concepts:
                allNewConcepts.append(oldC)
                # and we don't need to create a new object for it, so we jump
                next()

        newConcept = schemas.ConceptNew()
        newConcept.name = f"Concept {conceptCounter}"
        newConcept.dna = dnaString
        newConcept.treeID = treeID
        
        # add to DB:
        storage.new_EFMobject(db, 'concept', newConcept)

        allNewConcepts.append(newConcept)
        conceptCounter = conceptCounter + 1

    # delete old concepts:
    for oC in allOldConcepts:
        storage.delete_EFMobject(db, 'concept', oC.id)
        
    return allNewConcepts

def prune_child_ds(ds: schemas.DesignSolution, dna: List[int]):
    '''
        takes a DS and removes all child DS _not_ in dna (dna to be a list of int)
    '''
    for fr in ds.requires_functions:
        for childDS in fr.is_solved_by:
            # remove the DS not in DNA:
            if not childDS.id in dna:
                fr.is_solved_by.remove(childDS)
            else:
                # else prune the children, too
                childDS = prune_child_ds(ds, dna)

    return ds

def allChildDS(fr: schemas.FunctionalRequirement, childList = []):
    '''
        iterates through all children of an FR and 
        returns a list of DS 
    '''
    newChildList = childList

    for ds in fr.is_solved_by:
        newChildList.append(ds)

        for fr in ds.requires_functions:
            newChildList.extend(allChildDS(fr))

    return newChildList

def allChildFR(ds: schemas.DesignSolution, childList = []):
    '''
        iterates through all children of a DS and 
        returns a list of FR
    '''
    newChildList = childList

    for fr in ds.requires_functions:
        newChildList.append(fr)
        
        for ds in fr.is_solved_by:
            newChildList.extend(allChildFR(ds))

    return newChildList


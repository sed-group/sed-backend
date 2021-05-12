from sqlalchemy.orm import Session, lazyload, eagerload
from fastapi import HTTPException, status
from typing import List

from apps.EFMbackend.utils import not_yet_implemented

#import apps.EFMbackend.models as models
import apps.EFMbackend.parameters.schemas as schemas
import apps.EFMbackend.parameters.storage as storage
import apps.EFMbackend.storage as efmStorage
from apps.EFMbackend.exceptions import *

import json

### DP todo!! 
def get_DP(DPid: int):
    ''' 
        returns a DP object with all details
    '''
    return storage.get_DP(DPid)
    
    
def create_DP(newDP: schemas.DPnew):
    '''
        creates a new DP object as a child of a DS 
    '''
    # check if parent exists:
    try:
        parentDS = efmStorage.getDS(newDP.dsID)
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find parent DS with ID {}.".format(newDP.dsID)
        )

    # set treeID from parent DS:
    if not newDP.treeID:
        newDP.treeID = parentDS.treeID
    elif newDP.treeID != parentDS.treeID:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TreeID not identical with parentDS treeID"
        )

    # deposit in DB:
    return storage.new_DP(newDP)


def delete_DP(DPid: int):
    # check if exists:
    try:
        storage.get_DP(DPid)
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find DP with ID {}.".format(dpID)
        )
    
    return storage.delete_DP(dpID)

def edit_DP(DPid: int, DPdata: schemas.DPnew):
    return not_yet_implemented()

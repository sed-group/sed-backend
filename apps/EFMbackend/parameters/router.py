from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session
from typing import List

# from .models import *
#from apps.EFMbackend.database import SessionLocal
import apps.EFMbackend.parameters.implementation as implementation
import apps.EFMbackend.parameters.schemas as schemas

router = APIRouter()

## DP
@router.get("/dp/{DPid}",
            response_model = schemas.DesignParameter,
            summary="returns a single DP object -WIP-"
            )
async def get_designParameter(DPid: int):
    return implementation.get_DP(DPid = DPid)

@router.post("/dp",
            response_model = schemas.DesignParameter,
            summary="creates a new DP object",
            description="the json part of the post contains the DSid of the parent DS"
            )
async def create_designParameter( DSid: int, DPdata: schemas.DPnew):
    return implementation.create_DP(parentID = DSid, newDP= DPdata)

@router.delete("/dp/{DPid}",
            summary="deletes a DP object by id -WIP-"
            )
async def delete_designParameter(DPid: int):
    return implementation.delete_DP(DPid = DPid)

@router.put("/dp/{DPid}",
            response_model = schemas.DesignParameter,
            summary="edits an exisitng DP object via DPdata (json) -WIP-"
            )
async def edit_designParameter(DPid: int, DPdata: schemas.DPnew):
    return implementation.edit_DP(DPid = DPid)
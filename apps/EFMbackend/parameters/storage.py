from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session, lazyload, eagerload
from typing import List

from apps.EFMbackend.database import SessionLocal
from apps.EFMbackend.exceptions import EfmElementNotFoundException
import apps.EFMbackend.models as models
import apps.EFMbackend.parameters.schemas as schemas

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
        
def get_DP(DPid: int, db: Session = Depends(get_db)):
    '''
        fetches a DP via its id from the database
        returns schemas.DesignParameter or raises exception
    '''
    
    try:
        theDPorm = db.query(models.DesignParameter).filter(models.DesignParameter.id == DPid).first()
        if theDPorm:
            theDPpydantic = schemas.DesignParameter.from_orm(theDPorm)
            return theDPpydantic
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DP with ID {} does not exist.".format(DPid)
            )
    except EfmElementNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DS with ID {} does not exist.".format(DPid)
        )
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DPid needs to be an integer"
        )

def new_DP(DPdata: schemas.DPnew,  db: Session = Depends(get_db)):
    '''
    stores DPdata as a new DP object in the database
    returns a schemas.DesignParameter
    '''
    try: 
        theDPorm = models.DesignParameter(**DPdata.dict())
        db.add(obj)
        db.commit()

        theDPpydantic = schemas.DesignParameter.from_orm(theDPorm)
        return theDPpydantic
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database did not accept new DesignParameter."
        )

def delete_DP(DPid: int,  db: Session = Depends(get_db)):
    try:
        db.query(models.DesignParameter).filter(models.DesignParameter.id == DPid).delete()
        db.commit()
        return True
    except TypeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DPid needs to be an integer"
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database could not delete DesignParameter."
        )

def edit_DP(DPid: int, DPdata: schemas.DPnew,  db: Session = Depends(get_db)):
    try: 
        theDPorm = db.query(models.DesignParameter).filter(models.DesignParameter.id == DPid).first()
        
        # write values
        theDPorm.name = DPdata.name
        theDPorm.value = DPdata.value
        theDPorm.unit = DPdata.unit
        theDPorm.dsID = DPdata.dsID
        theDPorm.treeID = DPdata.treeID

        # and write to DB
        db.commit()

        # convert to pydantic
        theDPpydantic = schemas.DesignParameter.from_orm(theDPorm)
        return theDPpydantic
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database could not edit DesignParameter DPid{}".format(DPid)
        )
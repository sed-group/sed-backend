from datetime import datetime

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, ForwardRef


## DESIGN PARAMEERS
class DPnew(BaseModel):
    name: str
    value: Optional[str] = None
    unit: Optional[str] = 'm'
    treeID: Optional[int] = None
    dsID: int = None # parent DS

class DesignParameter(DPnew):
    id: int
    treeID: int
    
    class Config:
        orm_mode = True

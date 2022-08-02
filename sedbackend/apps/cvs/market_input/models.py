from pydantic import BaseModel
from sedbackend.apps.cvs.vcs import models as vcs_models


class MarketInputGet(BaseModel):
    id: int
    name: str
    unit: str

class MarketInputPost(BaseModel):
    name: str
    unit: str
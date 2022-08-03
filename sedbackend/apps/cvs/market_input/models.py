from pydantic import BaseModel
from sedbackend.apps.cvs.vcs import models as vcs_models


class MarketInputGet(BaseModel):
    id: int
    name: str
    unit: str

class MarketInputPost(BaseModel):
    name: str
    unit: str

######################################################################################################################
# Market Values
######################################################################################################################

class MarketValueGet(BaseModel):
    vcs_name: str
    market_input_id: int
    value: float
from typing import Optional, List

from pydantic import BaseModel


class ExternalFactor(BaseModel):
    id: int
    name: str
    unit: str


class ExternalFactorPost(BaseModel):
    name: str
    unit: str


######################################################################################################################
# Market Values
######################################################################################################################

class VcsEFValuePair(BaseModel):
    vcs_id: int
    value: float


# Combined External Factor and the connected value pairs of vcs and value
class ExternalFactorValue(BaseModel):
    id: int
    name: str
    unit: str
    external_factor_values: Optional[List[VcsEFValuePair]]

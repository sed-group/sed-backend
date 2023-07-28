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


class ExternalFactorValue(BaseModel):
    external_factor: ExternalFactor
    external_factor_value: Optional[List[VcsEFValuePair]]

from pydantic import BaseModel


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


class MarketInputValue(BaseModel):
    vcs_id: int
    market_input_id: int
    value: float

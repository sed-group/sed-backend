from pydantic import BaseModel


class MarketInputGet(BaseModel):
    id: int
    vcs: int
    node: int
    time: float
    cost: float
    revenue: float


class MarketInputPost(BaseModel):
    time: float
    cost: float
    revenue: float
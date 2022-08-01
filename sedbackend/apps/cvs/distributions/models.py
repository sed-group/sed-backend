from pydantic import BaseModel


class Distribution(BaseModel):
    approx_mean: float
    exact_mean: float
    approx_std: float
    exact_std: float

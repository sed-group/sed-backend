from pydantic import BaseModel
from enum import IntEnum, unique


@unique
class DesignParameterType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    BOOLEAN = 2
    STRING = 3


class DesignParameter(BaseModel):
    id: int
    name: str
    value: any
    type: DesignParameterType
    product_id: int


class Product(BaseModel):
    id: int
    name: str
    design_parameters: dict

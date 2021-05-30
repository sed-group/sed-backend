from typing import Optional, Any
from enum import IntEnum, unique, Enum
from datetime import datetime

from pydantic import BaseModel


@unique
class MeasurementDateClassification(Enum):
    INSERT = 'insert'
    MEASUREMENT = 'measurement'


@unique
class MeasurementDataType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    BOOLEAN = 2
    STRING = 3

    @staticmethod
    def get_parameter_type(value):
        t = value.__class__.__name__
        if t == 'int':
            return MeasurementDataType.INTEGER
        elif t == 'float':
            return MeasurementDataType.FLOAT
        elif t == 'bool':
            return MeasurementDataType.BOOLEAN
        elif t == 'str':
            return MeasurementDataType.STRING

        raise ValueError("Unhandled data type")


@unique
class MeasurementType(IntEnum):
    UNDEFINED = 0


class Measurement(BaseModel):
    id: int
    name: str
    type: int
    description: Optional[str]


class MeasurementPost(BaseModel):
    name: str
    type: int
    description: Optional[str]


class MeasurementResultData(BaseModel):
    id: int
    measurement_id: int
    value: Any
    type: MeasurementDataType
    insert_timestamp: datetime
    measurement_timestamp: Optional[datetime]


class MeasurementResultDataPost(BaseModel):
    value: Any
    type: MeasurementDataType
    measurement_timestamp: datetime


class MeasurementResultFile(BaseModel):
    id: int
    measurement_id: int
    file: str
    insert_timestamp: int


class MeasurementResultFilePost(BaseModel):
    measurement_id: int
    file: str
    insert_timestamp: int

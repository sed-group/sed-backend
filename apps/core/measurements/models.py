"""
Brief explanation of the structure hierarchy of measurement classes:

A measurement is similar to a "signal" of some sort. In itself, it contains no information other than what
is being measured. A measurement result may be a file, or raw data. A measurement set contains a collection of
measurements that are related somehow. For instance, a measurement set might contain measurements done on a particular
product/concept instance.
"""

from typing import Optional, Any, List
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
    COMPUTER_SIMULATION = 1
    LIVE_DATA = 2
    PREDICTED_DATA = 3

class Measurement(BaseModel):
    id: int
    name: str
    type: int
    description: Optional[str]
    measurement_set_id: int


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


@unique
class MeasurementSetType(IntEnum):
    UNDEFINED = 0
    MIXTURE = 1
    COMPUTER_SIMULATION = 2
    LIVE_DATA = 3
    PREDICTED_DATA = 4


class MeasurementSetListing(BaseModel):
    id: int
    name: str
    type: MeasurementSetType
    description: str
    measurement_count: int


class MeasurementSet(BaseModel):
    id: int
    name: str
    type: MeasurementSetType
    description: str
    measurements: Optional[List[Measurement]] = []


class MeasurementSetPost(BaseModel):
    name: str
    type: MeasurementSetType
    description: str

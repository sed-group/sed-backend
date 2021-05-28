from typing import Optional, Any

from pydantic import BaseModel


class Measurement(BaseModel):
    id: int
    name: str
    type: int


class MeasurementResultData(BaseModel):
    id: int
    measurement_id: int
    value: Any
    type: int
    insert_timestamp: int
    measurement_timestamp: int


class MeasurementResultFile(BaseModel):
    id: int
    measurement_id: int
    file: str
    insert_timestamp: int

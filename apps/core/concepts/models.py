from enum import IntEnum, unique
from typing import Optional, Any, Dict

from pydantic import BaseModel


@unique
class ParameterType(IntEnum):
    INTEGER: 0
    FLOAT: 1
    BOOLEAN: 2
    STRING: 3


class Concept(BaseModel):
    id: int
    name: str
    parameters: Dict[str, Any]      # Parameter name -> Parameter value


class ConceptParameter(BaseModel):
    id: int
    name: str
    type: ParameterType
    concept_id: int
    value: Any

    def get_parsed_value(self):
        if ParameterType is ParameterType.INTEGER:
            return int(self.value)
        elif ParameterType is ParameterType.FLOAT:
            return float(self.value)
        elif ParameterType is ParameterType.BOOLEAN:
            return bool(self.value)
        elif ParameterType is ParameterType.STRING:
            return str(self.value)


class ConceptArchetype(BaseModel):
    id: int
    name: str
    parameters: Dict[str, Any]


from enum import IntEnum, unique
from typing import Optional, Any, Dict

from fastapi.logger import logger
from pydantic import BaseModel


@unique
class ParameterType(IntEnum):
    INTEGER = 0
    FLOAT = 1
    BOOLEAN = 2
    STRING = 3

    @staticmethod
    def get_parameter_type(value):
        t = value.__class__.__name__

        logger.debug(f'Get parameter type of "{value}". Type = {t}')

        if t == 'int':
            return ParameterType.INTEGER
        elif t == 'float':
            return ParameterType.FLOAT
        elif t == 'bool':
            return ParameterType.BOOLEAN
        elif t == 'str':
            return ParameterType.STRING

        raise ValueError("Unhandled data type")


class Concept(BaseModel):
    id: int
    name: str
    parameters: Dict[str, Any]      # Parameter name -> Parameter value


class ConceptPost(BaseModel):
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


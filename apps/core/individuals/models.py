from enum import IntEnum, unique
from typing import Optional, Any, List

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


class IndividualParameterPost(BaseModel):
    name: str
    value: Any


class IndividualParameter(IndividualParameterPost):
    id: int
    name: str
    type: ParameterType
    value: Any
    individual_id: int

    def get_parsed_value(self):
        if self.type is ParameterType.INTEGER:
            return int(self.value)

        elif self.type is ParameterType.FLOAT:
            return float(self.value)

        elif self.type is ParameterType.BOOLEAN:
            # Handle numeric booleans (should not happen if API is used correctly)
            if self.value.isnumeric():
                if int(self.value) == 0:
                    return False
                else:
                    return True
            # Handle regular stringified boolean
            if str.upper(self.value) == "FALSE":
                return False
            return True

        elif self.type is ParameterType.STRING:
            return str(self.value)

        else:
            raise ValueError("I don't know what you want me to do with this.")


class IndividualArchetypePost(BaseModel):
    name: str
    parameters: Optional[List[IndividualParameterPost]] = []


class IndividualArchetype(BaseModel):
    id: int
    name: str
    parameters: List[IndividualParameter] = []


class IndividualPost(BaseModel):
    name: str
    archetype_id: Optional[int] = None
    parameters: Optional[List[IndividualParameterPost]] = []


class Individual(BaseModel):
    id: int
    name: str
    archetype_id: Optional[int] = None
    parameters: List[IndividualParameter] = []

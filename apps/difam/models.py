from typing import Optional, Union, List
from enum import IntEnum, unique
from datetime import datetime

from pydantic import BaseModel

from apps.core.users.models import User
from apps.core.individuals.models import IndividualArchetype


class DifamProjectPost(BaseModel):
    name: str
    individual_archetype_id: Optional[int] = None


class DifamProject(BaseModel):
    id: int
    name: str
    owner: User
    archetype: Optional[IndividualArchetype]
    datetime_created: datetime
    subproject_id: int


class RangeParameter(BaseModel):
    parameter_id: int
    lower_value: Union[int, float, bool]
    upper_value: Union[int, float, bool]


@unique
class DOEType(IntEnum):
    HYPERCUBE = 0
    FACTORIAL_2K = 1


class DOEGenerationRequest(BaseModel):
    doe_type: DOEType
    doe_experiment_count: int
    range_parameters: List[RangeParameter]

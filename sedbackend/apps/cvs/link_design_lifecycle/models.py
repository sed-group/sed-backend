from typing import List

from pydantic import BaseModel
from enum import Enum

from sedbackend.apps.cvs.market_input.models import MarketInputGet
from sedbackend.apps.cvs.vcs.models import ValueDriver


class TimeFormat(str, Enum):
    """
    The time formats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    MINUTES: str = 'minutes'
    HOUR: str = 'hour'
    DAY: str = 'day'
    WEEK: str = 'week'
    MONTH: str = 'month'
    YEAR: str = 'year'


class Rate(Enum):
    PRODUCT = 'per_product'
    PROJECT = 'per_project'


class FormulaGet(BaseModel):
    vcs_row_id: int
    design_group_id: int
    time: str
    time_unit: TimeFormat
    cost: str
    revenue: str
    rate: Rate
    value_drivers: List[ValueDriver] = []
    external_factors: List[MarketInputGet] = []


class FormulaPost(BaseModel):
    time: str
    time_unit: TimeFormat
    cost: str
    revenue: str
    rate: Rate
    value_drivers: List[int] = []
    external_factors: List[int] = []


class VcsDgPairs(BaseModel):
    vcs: str
    vcs_id: int
    design_group: str
    design_group_id: int
    has_formulas: int

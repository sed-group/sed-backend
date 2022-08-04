from sqlite3 import Time
from pydantic import BaseModel
from enum import Enum
from typing import List, Tuple

from sedbackend.apps.cvs.vcs import models as vcs_models
from sedbackend.apps.cvs.design import models as design_models
from sedbackend.apps.cvs.market_input import models as mi_models

class TimeFormat(Enum):
    """
    The timeformats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    HOUR = 365*24
    DAY = 365
    WEEK = 52
    MONTH = 12
    YEAR = 1

class Rate(Enum):
    PRODUCT = 'per_product'
    PROJECT = 'per_project'

class QuantifiedObjectivePost(BaseModel):
    value_driver_id: int
    design_group_id: int

class FormulaGet(BaseModel):
    vcs_row_id: int
    time: str
    time_unit: TimeFormat
    cost: str
    revenue: str
    rate: Rate
    

class FormulaPost(BaseModel):
    time: str
    time_unit: TimeFormat
    cost: str
    revenue: str
    rate: Rate
    quantified_objective_ids: List[QuantifiedObjectivePost]
    market_input_ids: List[int]


class FormulaRowGet(FormulaGet):
    quantified_objectives: List[design_models.QuantifiedObjective]
    market_inputs: List[mi_models.MarketInputGet]
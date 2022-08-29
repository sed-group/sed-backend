from sqlite3 import Time
from pydantic import BaseModel
from enum import Enum
from typing import List, Tuple, Optional

from sedbackend.apps.cvs.vcs import models as vcs_models
from sedbackend.apps.cvs.design import models as design_models
from sedbackend.apps.cvs.market_input import models as mi_models

class TimeFormat(Enum):
    """
    The timeformats that can be chosen for a process. The values are the defaults for the
    simulation (years)
    """
    MINUTES = 'minutes'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'

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
    

class FormulaPost(BaseModel):
    time: str
    time_unit: TimeFormat
    cost: str
    revenue: str
    rate: Rate
    value_driver_ids: Optional[List[int]] = None
    market_input_ids: Optional[List[int]] = None


class FormulaRowGet(FormulaGet):
    value_drivers: List[vcs_models.ValueDriver]
    market_inputs: List[mi_models.MarketInputGet]
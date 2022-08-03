from sqlite3 import Time
from pydantic import BaseModel
from enum import Enum
from typing import List

from sedbackend.apps.cvs.vcs import models as vcs_models
from sedbackend.apps.cvs.design import models as design_models

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

class FormulaGet(BaseModel):
    vcs_row: vcs_models.VcsRow
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


class FormulaRowGet(FormulaGet):
    quantified_objectives: List[design_models.QuantifiedObjective]
    #market_parameters: None #TODO add when that module is added
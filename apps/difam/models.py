from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class DifamProject(BaseModel):
    id: int
    name: str
    individual_archetype_id: Optional[int]
    owner_id: int
    datetime_created: datetime

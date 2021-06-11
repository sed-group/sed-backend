from typing import Optional
from datetime import datetime

from pydantic import BaseModel


class DifamProjectPost(BaseModel):
    name: str
    individual_archetype_id: Optional[int] = None


class DifamProject(DifamProjectPost):
    id: int
    owner_id: int
    datetime_created: datetime

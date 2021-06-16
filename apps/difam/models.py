from typing import Optional
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

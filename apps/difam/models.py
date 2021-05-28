from typing import Optional

from pydantic import BaseModel


class DifamProject(BaseModel):
    id: int
    concept_archetype_id: Optional[int]

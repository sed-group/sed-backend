from pydantic import BaseModel
from typing import Optional


class Application(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    href_api: Optional[str] = None      # Reference to associated API root endpoint

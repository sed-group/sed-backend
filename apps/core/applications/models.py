from pydantic import BaseModel
from typing import Optional


class Application(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    contact: Optional[str] = None
    href: Optional[str] = None          # Project homepage
    href_access: str                    # Front-end access point
    href_docs: Optional[str] = None     # Link to documentation
    href_source: Optional[str] = None   # Project repository
    href_api: Optional[str] = None      # Reference to associated API root endpoint

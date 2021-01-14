from pydantic import BaseModel


class Application(BaseModel):
    id: int
    name: str
    url: str
    description: str
    contact: str
    href: str               # Project homepage
    href_access: str        # Front-end access point
    href_docs: str          # Link to documentation
    href_source: str        # Project repository
    href_api:   str         # Reference to associated API root endpoint

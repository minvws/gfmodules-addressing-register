from typing import Optional
from pydantic import BaseModel

from app.data import EndpointStatus

class EndpointModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: str
    status_type: EndpointStatus

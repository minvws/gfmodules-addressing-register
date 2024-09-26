from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class CommonQueryParams(BaseModel):
    id: UUID | None = None
    last_updated: datetime | None = None

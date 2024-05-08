from typing import Optional

from pydantic import BaseModel


class Meta(BaseModel):
    total: int
    limit: Optional[int] = None
    offset: Optional[int] = None

from datetime import datetime

from pydantic import AliasChoices, BaseModel, Field


class HistoryRequest(BaseModel):
    since: datetime | None = Field(
        alias="_since",
        validation_alias=AliasChoices("since", "_since"),
        default=None,
    )

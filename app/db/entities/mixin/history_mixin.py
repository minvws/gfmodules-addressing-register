from typing import Any, Dict, Literal
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.entities.mixin.common_mixin import CommonMixin

FhirInteractions = Literal["create", "update", "delete"]


class HistoryMixin(CommonMixin):
    interaction: Mapped[FhirInteractions] = mapped_column(
        "interaction", Enum("create", "update", "delete", name="fhir_interactions")
    )
    data: Mapped[Dict[str, Any]] = mapped_column("data", JSONB)

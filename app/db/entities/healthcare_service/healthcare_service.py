from datetime import datetime
from typing import Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, types
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base


class HealthcareServiceEntry(Base):
    __tablename__ = "healthcare_services"
    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        default=uuid4,
        primary_key=True,
    )
    fhir_id: Mapped[str] = mapped_column("fhir_id", types.String(150))
    version: Mapped[int] = mapped_column("version", types.Integer, default=1)
    latest: Mapped[bool] = mapped_column("latest", types.Boolean, default=True)
    data: Mapped[Dict[str, Any]] = mapped_column("data", JSONB)
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )

from datetime import UTC, datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import BOOLEAN, INTEGER, TIMESTAMP, types
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class BaseMixin:
    created_at: Mapped[datetime] = mapped_column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now(UTC),
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )


class CommonMixin(BaseMixin):
    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        default=uuid4,
    )
    data: Mapped[Optional[Dict[str, Any]]] = mapped_column("data", JSONB)
    bundle_meta: Mapped[Dict[str, Any]] = mapped_column("bundle_meta", JSONB)
    fhir_id: Mapped[UUID] = mapped_column("fhir_id", types.Uuid)
    version: Mapped[int] = mapped_column("version", INTEGER, default=1)
    latest: Mapped[bool] = mapped_column(
        "latest", BOOLEAN, nullable=False, default=True
    )
    deleted: Mapped[bool] = mapped_column(
        "deleted", BOOLEAN, nullable=False, default=False
    )

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import TIMESTAMP, types
from sqlalchemy.orm import Mapped, mapped_column


class BaseMixin:
    created_at: Mapped[datetime] = mapped_column(
        "created_at", TIMESTAMP, nullable=False, default=datetime.now()
    )
    modified_at: Mapped[datetime] = mapped_column(
        "modified_at", TIMESTAMP, nullable=False, default=datetime.now()
    )


class CommonMixin(BaseMixin):
    id: Mapped[UUID] = mapped_column(
        "id",
        types.Uuid,
        nullable=False,
        default=uuid4,
    )

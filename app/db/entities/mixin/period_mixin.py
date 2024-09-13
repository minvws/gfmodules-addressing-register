from datetime import datetime
from uuid import UUID

from sqlalchemy import types, TIMESTAMP

from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.mixin.common_mixin import CommonMixin


class PeriodMixin(CommonMixin):
    id: Mapped[UUID] = mapped_column("id", types.UUID, primary_key=True)
    start_date: Mapped[datetime] = mapped_column("start_date", TIMESTAMP)
    end_date: Mapped[datetime] = mapped_column("end_date", TIMESTAMP)

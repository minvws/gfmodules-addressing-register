from typing import Any, Dict
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.entities.mixin.common_mixin import CommonMixin


class HistoryMixin(CommonMixin):
    data: Mapped[Dict[str, Any]] = mapped_column("data", JSON)

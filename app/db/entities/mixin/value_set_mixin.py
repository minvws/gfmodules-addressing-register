from sqlalchemy import String

from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.mixin.common_mixin import BaseMixin


class ValueSetMixin(BaseMixin):
    code: Mapped[str] = mapped_column(
        "code", String(50), nullable=False, primary_key=True
    )
    definition: Mapped[str] = mapped_column("definition", String(255), nullable=False)
    display: Mapped[str] = mapped_column("display", String(150), nullable=False)

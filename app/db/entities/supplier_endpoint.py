from sqlalchemy import PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.entities.base import Base
from app.db.entities.mixin.common_mixin import BaseMixin


class SupplierEndpoint(BaseMixin, Base):
    __tablename__ = "supplier_endpoints"
    __table_args__ = (PrimaryKeyConstraint("ura_number"),)

    ura_number: Mapped[str] = mapped_column("ura_number", String(8), nullable=False, unique=True)
    care_provider_name: Mapped[str] = mapped_column("care_provider_name", String(150), nullable=False)
    update_supplier_endpoint: Mapped[str] = mapped_column("update_supplier_endpoint", String, nullable=False)

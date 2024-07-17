from typing import Any

from sqlalchemy import String, JSON
from sqlalchemy.orm import mapped_column, Mapped
from app.db.entities.base import Base


class AddressEntity(Base):
    __tablename__ = "addresses"

    ura_number: Mapped[str] = mapped_column(
        "ura_number", String, primary_key=True, nullable=False
    )
    data_domain: Mapped[str] = mapped_column(
        "data_domain", String, primary_key=True, nullable=False
    )
    endpoint: Mapped[str] = mapped_column("endpoint", String, nullable=False)
    request_type: Mapped[str] = mapped_column("request_type", String, nullable=False)
    parameters: Mapped[list[dict[str, Any]]] = mapped_column("parameters", JSON, nullable=False)

    def __repr__(self) -> str:
        return f"<AddressEntity(ura_number={self.ura_number}, data_domain={self.data_domain} endpoint={self.endpoint}, request_type={self.request_type}, parameters = {self.parameters})>"

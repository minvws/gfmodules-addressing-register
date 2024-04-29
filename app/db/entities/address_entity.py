from sqlalchemy import String, JSON
from sqlalchemy.orm import mapped_column, Mapped
from app.db.entities.base import Base


class AddressEntity(Base):
    __tablename__ = "addresses"

    provider_id: Mapped[str] = mapped_column(
        "provider_id", String, primary_key=True, nullable=False
    )
    data_domain: Mapped[str] = mapped_column(
        "data_domain", String, primary_key=True, nullable=False
    )
    endpoint: Mapped[str] = mapped_column("endpoint", String, nullable=False)
    request_type: Mapped[str] = mapped_column("request_type", String, nullable=False)
    parameters: Mapped[JSON] = mapped_column("parameters", JSON, nullable=False)

    def __repr__(self) -> str:
        return f"<Example(provider_id={self.provider_id}, data_domain={self.data_domain} endpoint={self.endpoint}, request_type={self.request_type}, parameters = {self.parameters})>"

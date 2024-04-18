from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped
from app.db.models.base import Base


class Example(Base):
    __tablename__ = "examples"

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("name", String(100), nullable=False)

    def __repr__(self) -> str:
        return f"<Example(id={self.id}, name={self.name})>"

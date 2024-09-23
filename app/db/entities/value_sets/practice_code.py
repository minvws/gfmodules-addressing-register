from app.db.entities.mixin.value_set_mixin import ValueSetMixin
from app.db.entities.base import Base


class PracticeCode(ValueSetMixin, Base):
    __tablename__ = "practice_codes"

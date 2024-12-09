from abc import ABCMeta, abstractmethod
from typing import Any, Sequence

from app.db.db import Database
from app.db.entities.base import Base


class EntityService(metaclass=ABCMeta):
    def __init__(self, database: Database):
        self.database = database

    @abstractmethod
    def find(self, *args: Any, **kwargs: Any) -> Sequence[Base]: ...

    @abstractmethod
    def get_one(self, *args: Any, **kwargs: Any) -> Base: ...

    @abstractmethod
    def add_one(self, *args: Any, **kwargs: Any) -> Base: ...

    @abstractmethod
    def update_one(self, *args: Any, **kwargs: Any) -> Base: ...

    @abstractmethod
    def delete_one(self, *args: Any, **kwargs: Any) -> None: ...

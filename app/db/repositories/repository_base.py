from typing import TypeVar
from sqlalchemy.orm import Session


class RepositoryBase:
    def __init__(self, session: Session) -> None:
        self.session = session


TRepositoryBase = TypeVar("TRepositoryBase", bound=RepositoryBase, covariant=True)

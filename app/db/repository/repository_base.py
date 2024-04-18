from sqlalchemy.orm import Session


class RepositoryBase:
    def __init__(self, session: Session) -> None:
        self.session = session

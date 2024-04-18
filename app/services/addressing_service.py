from app.db.db import Database


class AddressingService:
    def __init__(self, database: Database):
        self.database = database

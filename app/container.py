import inject
from db.db import Database
from config import get_config
from app.services.addressing_service import AddressingService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn)
    binder.bind(Database, db)
    addressing_service = AddressingService(db)
    binder.bind(AddressingService, addressing_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_addressing_service() -> AddressingService:
    return inject.instance(AddressingService)


if not inject.is_configured():
    inject.configure(container_config)

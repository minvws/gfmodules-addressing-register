import inject
from app.db.db import Database
from app.config import get_config
from app.services.addressing_service import AddressingService
from app.services.endpoint_service import EndpointService
from app.services.organization_service import OrganizationService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn)
    binder.bind(Database, db)
    addressing_service = AddressingService(db)
    binder.bind(AddressingService, addressing_service)
    organization_service = OrganizationService(db)
    binder.bind(OrganizationService, organization_service)
    endpoint_service = EndpointService(db)
    binder.bind(EndpointService, endpoint_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_addressing_service() -> AddressingService:
    return inject.instance(AddressingService)

def get_organization_service() -> OrganizationService:
    return inject.instance(OrganizationService)

def get_endpoint_service() -> EndpointService:
    return inject.instance(EndpointService)

if not inject.is_configured():
    inject.configure(container_config)

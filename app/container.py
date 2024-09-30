import inject
from app.db.db import Database
from app.config import get_config
from app.services.matching_care_service import MatchingCareService
from app.services.addressing_service import AddressingService
from app.services.endpoint_service import EndpointService
from app.services.organization_service import OrganizationService
from app.services.supplier_service import SupplierService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn, create_tables=config.database.create_tables)
    binder.bind(Database, db)

    addressing_service = AddressingService(db)
    binder.bind(AddressingService, addressing_service)

    organization_service = OrganizationService(db)
    binder.bind(OrganizationService, organization_service)

    endpoint_service = EndpointService(db)
    binder.bind(EndpointService, endpoint_service)

    supplying_service = SupplierService(db)
    binder.bind(SupplierService, supplying_service)

    matching_care_service = MatchingCareService(organization_service, endpoint_service)
    binder.bind(MatchingCareService, matching_care_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_addressing_service() -> AddressingService:
    return inject.instance(AddressingService)


def get_organization_service() -> OrganizationService:
    return inject.instance(OrganizationService)


def get_endpoint_service() -> EndpointService:
    return inject.instance(EndpointService)


def get_supplying_service() -> SupplierService:
    return inject.instance(SupplierService)


def get_matching_care_service() -> MatchingCareService:
    return inject.instance(MatchingCareService)


def setup_container() -> None:
    if not inject.is_configured():
        inject.configure(container_config)

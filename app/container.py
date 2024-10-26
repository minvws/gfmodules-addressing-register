import inject
from app.db.db import Database
from app.config import get_config
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.matching_care_service import MatchingCareService
from app.services.organization_history_service import OrganizationHistoryService
from app.services.supplier_service import SupplierService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(dsn=config.database.dsn, create_tables=config.database.create_tables)
    binder.bind(Database, db)

    supplying_service = SupplierService(db)
    binder.bind(SupplierService, supplying_service)

    organization_history_service = OrganizationHistoryService(db)
    binder.bind(OrganizationHistoryService, organization_history_service)

    endpoint_service = EndpointService(db, organization_history_service)
    organization_service = OrganizationService(db, organization_history_service)
    matching_care_service = MatchingCareService(organization_service, endpoint_service, organization_history_service)
    binder.bind(MatchingCareService, matching_care_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_supplying_service() -> SupplierService:
    return inject.instance(SupplierService)


def get_matching_care_service() -> MatchingCareService:
    return inject.instance(MatchingCareService)


def setup_container() -> None:
    inject.configure(container_config, once=True)

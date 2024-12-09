import inject
from app.db.db import Database
from app.config import get_config
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.entity_services.organization_affiliation_service import OrganizationAffiliationService
from app.services.entity_services.healthcare_service_service import HealthcareServiceService
from app.services.matching_care_service import MatchingCareService
from app.services.supplier_service import SupplierService


def container_config(binder: inject.Binder) -> None:
    config = get_config()

    db = Database(config=config.database)
    binder.bind(Database, db)

    supplying_service = SupplierService(db)
    binder.bind(SupplierService, supplying_service)

    endpoint_service = EndpointService(db)
    binder.bind(EndpointService, endpoint_service)

    organization_affiliation_service = OrganizationAffiliationService(db)
    binder.bind(OrganizationAffiliationService, organization_affiliation_service)

    healthcare_service_service = HealthcareServiceService(db)
    binder.bind(HealthcareServiceService, healthcare_service_service)

    organization_service = OrganizationService(db)
    binder.bind(OrganizationService, organization_service)

    matching_care_service = MatchingCareService(
        organization_service, endpoint_service
    )
    binder.bind(MatchingCareService, matching_care_service)


def get_database() -> Database:
    return inject.instance(Database)


def get_supplying_service() -> SupplierService:
    return inject.instance(SupplierService)


def get_organization_service() -> OrganizationService:
    return inject.instance(OrganizationService)


def get_endpoint_service() -> EndpointService:
    return inject.instance(EndpointService)


def get_organization_affiliation_service() -> OrganizationAffiliationService:
    return inject.instance(OrganizationAffiliationService)


def get_healthcare_service_service() -> HealthcareServiceService:
    return inject.instance(HealthcareServiceService)


def get_matching_care_service() -> MatchingCareService:
    return inject.instance(MatchingCareService)


def setup_container() -> None:
    inject.configure(container_config, once=True)

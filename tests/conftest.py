import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application import create_fastapi_app
from app.config import set_config
from app.container import get_database
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.matching_care_service import MatchingCareService
from test_config import get_test_config
from utils import init_database_with_types


@pytest.fixture(scope="module")
def app() -> FastAPI:
    set_config(get_test_config())
    app = create_fastapi_app()
    init_database_with_types()
    return app


@pytest.fixture(scope="module")
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="module")
def endpoint_service() -> EndpointService:
    return EndpointService(get_database())


@pytest.fixture(scope="module")
def organization_service() -> OrganizationService:
    return OrganizationService(get_database())


@pytest.fixture(scope="module")
def matching_care_service(
    organization_service: OrganizationService, endpoint_service: EndpointService
) -> MatchingCareService:
    return MatchingCareService(organization_service, endpoint_service)


@pytest.fixture
def org_endpoint() -> str:
    return "/Organization"


@pytest.fixture
def endpoint_endpoint() -> str:
    return "/Endpoint/"

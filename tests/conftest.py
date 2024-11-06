from typing import Generator

import inject
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application import create_fastapi_app
from app.config import set_config
from app.db.db import Database
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.matching_care_service import MatchingCareService
from app.services.organization_history_service import OrganizationHistoryService
from test_config import get_test_config_with_postgres_db_connection, get_postgres_database


@pytest.fixture
def app() -> Generator[FastAPI, None, None]:
    set_config(get_test_config_with_postgres_db_connection())
    app = create_fastapi_app()
    yield app
    inject.clear()


@pytest.fixture
def setup_database() -> Database:
    try:
        # first use the database from the injector
        db = inject.instance(Database)
        return db
    except inject.InjectorException:
        pass

    # else use the testing database
    return get_postgres_database()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture
def history_service(setup_database: Database) -> OrganizationHistoryService:
    return OrganizationHistoryService(setup_database)


@pytest.fixture
def endpoint_service(setup_database: Database, history_service: OrganizationHistoryService) -> EndpointService:
    return EndpointService(setup_database, history_service)


@pytest.fixture
def organization_service(setup_database: Database, history_service: OrganizationHistoryService) -> OrganizationService:
    return OrganizationService(setup_database, history_service)


@pytest.fixture
def matching_care_service(
    organization_service: OrganizationService, endpoint_service: EndpointService,
    history_service: OrganizationHistoryService
) -> MatchingCareService:
    return MatchingCareService(organization_service, endpoint_service, history_service)


@pytest.fixture
def org_endpoint() -> str:
    return "/Organization"


@pytest.fixture
def endpoint_endpoint() -> str:
    return "/Endpoint/"

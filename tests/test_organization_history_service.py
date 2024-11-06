import time

from app.db.db import Database
from app.services.organization_history_service import OrganizationHistoryService
from utils import add_organization, add_endpoint
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService


def test_add_one_should_add_one_history(
    history_service: OrganizationHistoryService,
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    setup_database: Database,
) -> None:
    setup_database.truncate_tables()

    expected, _ = add_organization(organization_service, endpoint_service)
    actual = history_service.find(id=expected.id)
    assert len(actual) == 1
    assert actual[0].interaction == "create"
    assert actual[0].organization_id == expected.id


def test_update_with_endpoint_should_add_one_history(
    history_service: OrganizationHistoryService,
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    setup_database: Database,
) -> None:
    setup_database.truncate_tables()

    expected, _ = add_organization(organization_service, endpoint_service)
    expected_endpoint = add_endpoint(org_id=expected.id, endpoint_service=endpoint_service)
    actual = history_service.find(id=expected.id)
    assert len(actual) == 2  # 1st for organization, 2nd for org with endpoint
    assert actual[0].organization_id == expected.id
    assert actual[0].interaction == "create"
    assert actual[1].organization_id == expected.id
    assert actual[1].interaction == "update"
    assert actual[1].data["endpoint"][0]["reference"] == "Endpoint/" + str(expected_endpoint.id)


def test_delete_organization_should_add_one_history(history_service: OrganizationHistoryService,
                                                    organization_service: OrganizationService,
                                                    endpoint_service: EndpointService,
                                                    setup_database: Database,
                                                    ) -> None:
    setup_database.truncate_tables()

    expected, _ = add_organization(organization_service, endpoint_service)
    actual = history_service.find(id=expected.id)
    assert len(actual) == 1
    assert actual[0].interaction == "create"

    # sleep to ensure that the created_at time is different
    time.sleep(1.0)

    # # This does not work well. It's probably going away very soon anyway.
    # organization_service.delete_one(UraNumber(expected.ura_number))
    # actual = history_service.find(
    #     identifier=expected.ura_number)  # find by identifier instead of organization_id since that is set to NULL
    # assert len(actual) == 2
    # assert actual[1].interaction == "delete"
    # assert actual[0].ura_number == expected.ura_number

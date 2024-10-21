# Helper function to check whether Bundle result contains the correct key and value
import random
from typing import Any, Optional
from uuid import UUID

from faker import Faker

from app.data import ConnectionType, EndpointStatus, UraNumber
from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization.organization import Organization
from app.models.organization.model import OrganizationModel
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.container import get_database
from app.db.entities.value_sets.endpoint_payload_types import EndpointPayloadType
from app.db.entities.value_sets.connection_type import (
    ConnectionType as ConnectionTypeEntity,
)

fake = Faker("nl_nl")


def check_key_value(
    data: dict[Any, Any] | list[Any], key_to_check: Any, value_to_check: Any
) -> bool:
    """
    Recursively checks if the specified key exists in the dictionary or list
    and if its value matches the specified value.

    Args:
        data: The dictionary or list to check.
        key_to_check: The key to look for.
        value_to_check: The value to check against.

    Returns:
        bool: True if the key is found with the specified value, otherwise False.
    """
    if isinstance(data, dict):
        return any(
            (key == key_to_check and value == value_to_check)
            or (
                isinstance(value, (dict, list))
                and check_key_value(value, key_to_check, value_to_check)
            )
            for key, value in data.items()
        )
    if isinstance(data, list):
        return any(check_key_value(item, key_to_check, value_to_check) for item in data)


def init_database_with_types() -> None:
    with get_database().get_db_session() as session:
        session.add(
            ConnectionTypeEntity(
                code="dicom-wado-rs", display="some_display", definition="some_def"
            )
        )
        session.add(EndpointPayloadType(code="none", definition="none", display="none"))
        session.commit()


# Helper function to add an organization
def add_organization(
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    active: Optional[bool] = None,
    ura_number: Optional[int] = None,
    name: Optional[str] = None,
    parent_organization: Optional[bool] = None,
    include: Optional[str] = None,
) -> tuple[Organization, Endpoint | None]:
    parent_organization_id: Optional[Organization] = None
    endpoint = None
    if parent_organization is True:
        parent_organization_id = add_organization(
            parent_organization=None,
            organization_service=organization_service,
            endpoint_service=endpoint_service,
        )[0]

    organization = organization_service.add_one(
        OrganizationModel(
            ura_number=UraNumber(ura_number)
            if ura_number is not None
            else UraNumber(fake.random_int(11111111, 99999999)),
            active=active if active is not None else fake.boolean(50),
            name=name or fake.text(50),
            description=fake.text(50),
            parent_organization_id=parent_organization_id.id
            if parent_organization and parent_organization_id is not None
            else None,
        )
    )

    if include is not None:
        endpoint = add_endpoint(
            org_id=organization.id, endpoint_service=endpoint_service
        )
    return organization, endpoint


# Helper function to add an endpoint
def add_endpoint(org_id: UUID, endpoint_service: EndpointService) -> Endpoint:
    endpoint = endpoint_service.add_one(
        name=fake.text(50),
        description=fake.text(50),
        address=fake.url(),
        status_type=random.choice(list(EndpointStatus)),
        organization_id=org_id,
        connection_type=ConnectionType.DicomWadoRs,
        payload_type="none",
        payload_mime_type="application/json",
    )
    return endpoint

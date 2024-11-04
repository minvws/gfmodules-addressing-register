import random
from datetime import datetime
from typing import List

from faker import Faker
from sqlalchemy import select

from app.config import get_config
from app.data import EndpointStatus, ConnectionType
from app.db.db import Database
from app.db.entities.contact_point.contact_point import ContactPoint
from app.db.entities.endpoint import (
    endpoint_contact_point,
    endpoint_environment,
    endpoint_header,
)
from app.db.entities.organization import (
    organization_contact,
    organization_type_association,
)
from app.db.entities.value_sets import (
    contact_point_system,
    contact_point_use,
    contact_type,
    environment,
    organization_type,
)
from app.models.organization.model import OrganizationModel
from app.models.supplier.model import SupplierModel
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.organization_history_service import OrganizationHistoryService
from app.services.supplier_service import SupplierService

fake = Faker("nl_nl")

config = get_config()
db = Database(config=config.database)


def run():
    organization_history_service = OrganizationHistoryService(db)
    organization_service = OrganizationService(
        database=db, history_service=organization_history_service
    )
    endpoint_service = EndpointService(
        database=db, organization_history_service=organization_history_service
    )

    org_ids = []
    endpoints_ids = []

    # Set up default metadata resource endpoint NEEDED FOR TIMELINE SERVICE
    default_org = organization_service.add_one(
        OrganizationModel(
            ura_number="23665292",
            active=True,
            name=fake.company(),
            description=fake.text(50),
            parent_organization_id=None,
        )
    )
    default_endpoint = endpoint_service.add_one(
        name=fake.text(20),
        description=fake.text(50),
        address="http://metadata:8503/resource",
        identifier=str(fake.random_int(0, 89999999, 1)),
        status_type=EndpointStatus.Active,
        organization_id=default_org.id,
        connection_type=random.choice(list(ConnectionType)),
        payload_type="none",
        payload_mime_type=fake.mime_type(),
    )
    org_ids.append(default_org.id)
    endpoints_ids.append(default_endpoint.id)
    default_org = organization_service.add_one(
        OrganizationModel(
            ura_number="13873620",
            active=True,
            name=fake.company(),
            description=fake.text(50),
            parent_organization_id=None,
        )
    )
    default_endpoint = endpoint_service.add_one(
        name=fake.text(20),
        description=fake.text(50),
        identifier=str(fake.random_int(0, 89999999, 1)),
        address="http://metadata:9999/resource",
        status_type=EndpointStatus.Active,
        organization_id=default_org.id,
        connection_type=random.choice(list(ConnectionType)),
        payload_type="none",
        payload_mime_type=fake.mime_type(),
    )
    org_ids.append(default_org.id)
    endpoints_ids.append(default_endpoint.id)

    for x in range(10):
        organization_model = OrganizationModel(
            ura_number=fake.random_int(0, 89999999, 1),
            active=fake.boolean(75),
            name=fake.company(),
            description=fake.text(50),
            parent_organization_id=(
                random.choice(org_ids)
                if fake.boolean(50) and len(org_ids) > 3
                else None
            ),
        )
        org = organization_service.add_one(organization_model)
        org_ids.append(org.id)
        ura_number = org.ura_number

        endpoint = endpoint_service.add_one(
            name=fake.text(20),
            description=fake.text(50),
            address=fake.url(),
            identifier=str(fake.random_int(0, 89999999, 1)),
            status_type=random.choice(list(EndpointStatus)),
            organization_id=org_ids[x + 2],
            connection_type=random.choice(list(ConnectionType)),
            payload_type="none",
            payload_mime_type=fake.mime_type(),
        )
        endpoints_ids.append(endpoint.id)

        supplier_model = SupplierModel(
            ura_number=ura_number,
            care_provider_name=fake.text(50),
            update_supplier_endpoint=fake.url(),
        )
        supplier_service = SupplierService(database=db)
        supplier_service.add_one(supplier_model)

    mass_session_commit(endpoints_ids=endpoints_ids, org_ids=org_ids)
    generate_endpoint_contact_points(endpoints_ids)


# Utility functions to fetch codes
def get_codes(model) -> List:
    with db.get_db_session() as session:
        stmt = select(model.code)
        return session.execute(stmt).scalars().all()


def mass_session_commit(endpoints_ids: List, org_ids: List) -> None:
    for x in range(len(endpoints_ids)):
        with db.get_db_session() as session:
            session.add(
                endpoint_header.EndpointHeader(
                    endpoint_id=endpoints_ids[x],
                    data=fake.text(50),
                )
            )
            session.add(
                endpoint_environment.EndpointEnvironment(
                    endpoint_id=endpoints_ids[x],
                    environment_type=random.choice(
                        list(get_codes(environment.Environment))
                    ),
                )
            )
            session.add(
                organization_type_association.OrganizationTypeAssociation(
                    organization_id=org_ids[x],
                    organization_type=random.choice(
                        list(get_codes(organization_type.OrganizationType))
                    ),
                )
            )
            session.add(
                organization_contact.OrganizationContact(
                    organization_id=org_ids[x],
                    contact_type=random.choice(
                        list(get_codes(contact_type.ContactType))
                    ),
                )
            )
            contact_point = ContactPoint(
                system_type=random.choice(
                    list(get_codes(contact_point_system.ContactPointSystem))
                ),
                use_type=random.choice(
                    list(get_codes(contact_point_use.ContactPointUse))
                ),
                value=fake.text(50),
                rank=fake.random_int(1, 5),
                period_start_date=fake.date_time_between(
                    start_date=datetime(2020, 1, 1), end_date=datetime(2022, 1, 1)
                ),
                period_end_date=fake.date_time_between(
                    start_date=datetime(2022, 1, 2), end_date=datetime(2024, 1, 1)
                ),
            )
            session.add(contact_point)
            session.commit()


def get_contact_points() -> List:
    with db.get_db_session() as session:
        stmt = select(ContactPoint.id)
        contact_points = session.execute(stmt).scalars().all()
        return contact_points


def generate_endpoint_contact_points(endpoints_ids: List) -> None:
    contact_points = get_contact_points()
    for x in range(len(endpoints_ids)):
        with db.get_db_session() as session:
            session.add(
                endpoint_contact_point.EndpointContactPoint(
                    endpoint_id=endpoints_ids[x],
                    contact_point_id=random.choice(list(contact_points)),
                )
            )
            session.commit()


if __name__ == "__main__":
    run()

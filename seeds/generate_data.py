from uuid import UUID, uuid4

from faker import Faker
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.organization import OrganizationContact
from fhir.resources.R4B.reference import Reference

from app.config import get_config
from app.db.db import Database
from app.models.supplier.model import SupplierModel
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.supplier_service import SupplierService


class DataGenerator:
    fake: Faker
    db: Database
    organization_service: OrganizationService
    endpoint_service: EndpointService
    supplier_service: SupplierService
    default_uras: list[str]
    default_metadata_urls: list[str]

    def __init__(self) -> None:
        self.fake = Faker()

        config = get_config()
        self.db = Database(config=config.database)
        self.organization_service = OrganizationService(self.db)
        self.endpoint_service = EndpointService(self.db)
        self.supplier_service = SupplierService(self.db)

        self.default_uras = ["23665292", "13873620"]
        self.default_metadata_urls = [
            "http://metadata:8503/resource",
            "http://metadata:9999/resource",
        ]

    def run(self):
        organization_uras = self.default_uras + [
            str(self.fake.random_number(8, True)) for _ in range(10)
        ]
        parent_org_id = None

        for ura_number in organization_uras:
            supplier_endpoint = self.generate_care_provider_endpoint_supplier(
                ura_number=ura_number
            )
            self.supplier_service.add_one(supplier_endpoint)
            endpoint = self.generate_endpoint()
            endpoint_entity = self.endpoint_service.add_one(endpoint)
            org = self.generate_organization(
                ura_number=ura_number,
                part_of=parent_org_id if parent_org_id is not None and self.fake.boolean(50) else None,
                endpoint_id=endpoint_entity.fhir_id,
            )
            self.organization_service.add_one(org)
            
            parent_org_id = org.id

    def generate_care_provider_endpoint_supplier(
        self,
        ura_number: str | None = None,
        care_provider_name: str | None = None,
        update_supplier_endpoint: str | None = None,
    ) -> SupplierModel:
        return SupplierModel(
            ura_number=ura_number
            if ura_number
            else str(self.fake.random_number(8, True)),
            care_provider_name=care_provider_name
            if care_provider_name
            else self.fake.company(),
            update_supplier_endpoint=update_supplier_endpoint
            if update_supplier_endpoint
            else self.fake.url(),
        )

    def generate_organization(
        self,
        ura_number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        uuid_identifier: str | None = None,
        endpoint_id: UUID | None = None,
        part_of: UUID | None = None,
    ) -> Organization:
        return Organization(
            identifier=[
                (
                    Identifier(
                        system="http://example.org/org", value=str(uuid_identifier)
                    )
                    if uuid_identifier
                    else Identifier(system="http://example.org/org", value=str(uuid4()))
                ),
                (
                    Identifier(
                        system="http://fhir.nl/fhir/NamingSystem/ura", value=ura_number
                    )
                    if ura_number is not None
                    else Identifier(
                        system="http://fhir.nl/fhir/NamingSystem/ura",
                        value=str(self.fake.random_number(8, True)),
                    )
                ),
            ],
            active=active if active is not None else self.fake.boolean(),
            type=[
                CodeableConcept(
                    coding=[
                        Coding(
                            system="http://example.org/org-type",
                            code=self.fake.random_element(
                                elements=("hospital", "clinic", "pharmacy", "lab")
                            ),
                            display=self.fake.random_element(
                                elements=("Hospital", "Clinic", "Pharmacy", "Lab")
                            ),
                        )
                    ]
                )
            ],
            name=name if name is not None else self.fake.company(),
            contact=[self.generate_fake_contact()],
            address=[self.generate_address()],
            endpoint=[{"reference": f"Endpoint/{endpoint_id}"}]
            if endpoint_id is not None
            else None,
            partOf={"reference": f"Organization/{part_of}"} if part_of is not None else None,
        )

    def generate_fake_contact(self) -> OrganizationContact:
        return OrganizationContact(
            name=HumanName(
                use=self.fake.random_element(
                    elements=(
                        "usual",
                        "official",
                        "temp",
                        "nickname",
                        "anonymous",
                        "old",
                        "maiden",
                    )
                ),
                text=self.fake.name(),
                family=self.fake.last_name(),
                given=[self.fake.first_name()],
            ),
            address=self.generate_address(),
        )

    def generate_address(self):
        return Address(
            use=self.fake.random_element(
                elements=("home", "work", "temp", "old", "billing")
            ),
            type=self.fake.random_element(elements=("postal", "physical", "both")),
            text=self.fake.address(),
            city=self.fake.city(),
            state=self.fake.state_abbr(),
            postalCode=self.fake.postcode(),
            country=self.fake.country(),
        )


    def generate_endpoint(
        self,
        org_fhir_id: UUID | None = None,
        status: str | None = None,
        name: str | None = None,
        uuid_identifier: UUID | None = None,
        endpoint_url: str | None = None,
    ) -> Endpoint:
        return Endpoint(
            identifier=[
                (
                    Identifier(
                        system="http://example.org/endpoint", value=str(uuid_identifier)
                    )
                    if uuid_identifier
                    else Identifier(
                        system="http://example.org/endpoint", value=str(uuid4())
                    )
                ),
            ],
            connectionType=Coding(
                system="http://example.org/connection-type",
                code=self.fake.random_element(
                    elements=("hl7-fhir-rest", "hl7-fhir-messaging")
                ),
                display=self.fake.random_element(
                    elements=("HL7 FHIR REST", "HL7 FHIR Messaging")
                ),
            ),
            name=name if name else self.fake.company(),
            payloadType=[
                CodeableConcept(
                    coding=[
                        Coding(
                            system="http://example.org/payload-type",
                            code=self.fake.random_element(
                                elements=(
                                    "application/fhir+json",
                                    "application/fhir+xml",
                                )
                            ),
                            display=self.fake.random_element(
                                elements=("FHIR JSON", "FHIR XML")
                            ),
                        )
                    ]
                )
            ],
            managingOrganization=Reference.construct(
                reference="Organization/" + str(org_fhir_id)
            )
            if org_fhir_id
            else None,
            address=self.fake.uri() if endpoint_url is None else endpoint_url,
            header=[
                self.fake.random_element(
                    elements=(
                        "Authorization: Bearer token",
                        "Content-Type: application/fhir+json",
                    )
                )
            ],
            payloadMimeType=[
                self.fake.random_element(
                    elements=("application/fhir+json", "application/fhir+xml")
                )
            ],
            status=(
                status
                if status
                else self.fake.random_element(
                    elements=("active", "suspended", "error", "off", "entered-in-error")
                )
            ),
        )


if __name__ == "__main__":
    generator = DataGenerator()
    generator.run()

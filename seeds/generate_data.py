from typing import Optional
from typing import List
from uuid import UUID, uuid4

from faker import Faker
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.fhirtypes import Id
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.location import Location
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.organizationaffiliation import OrganizationAffiliation
from fhir.resources.R4B.organization import OrganizationContact
from fhir.resources.R4B.practitioner import Practitioner, PractitionerQualification
from fhir.resources.R4B.practitionerrole import PractitionerRole
from fhir.resources.R4B.reference import Reference
from fhir.resources.healthcareservice import HealthcareService

from app.config import get_config
from app.db.db import Database
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService


class DataGenerator:
    fake: Faker
    db: Database
    organization_service: OrganizationService
    endpoint_service: EndpointService
    default_uras: list[str]
    default_metadata_urls: list[str]

    def __init__(self) -> None:
        self.fake = Faker()

        config = get_config()
        self.db = Database(config=config.database)
        self.organization_service = OrganizationService(self.db)
        self.endpoint_service = EndpointService(self.db)

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
            endpoint = self.generate_endpoint(
                endpoint_url=self.default_metadata_urls.pop(0) if len(self.default_metadata_urls) > 0 else None
            )
            endpoint_entity = self.endpoint_service.add_one(endpoint)
            org = self.generate_organization(
                ura_number=ura_number,
                part_of=parent_org_id if parent_org_id is not None and self.fake.boolean(50) else None,
                endpoint_id=endpoint_entity.fhir_id,
            )
            self.organization_service.add_one(org)

            parent_org_id = org.id

    def generate_organization_affiliation(
        self,
        active: bool | None = None,
        organization: UUID | None = None,
        participation_organization: UUID | None = None,
    ) -> OrganizationAffiliation:
        return OrganizationAffiliation(
            active=active if active is not None else self.fake.boolean(),
            organization={"reference": f"Organization/{organization}"} if organization is not None else None,
            participatingOrganization={"reference": f"Organization/{participation_organization}"} if participation_organization is not None else None,
        )


    def generate_location(
        self,
        organization: UUID | None = None,
        part_of: UUID | None = None,
    ) -> Location:
        return Location(
            managingOrganization={"reference": f"Organization/{organization}"} if organization is not None else None,
            partOf={"reference": f"Location/{part_of}"} if part_of is not None else None,
        )


    def generate_practitioner(
        self,
        active: bool | None = None,
        qualifications: Optional[list[UUID]] = None,
    ) -> Practitioner:
        q = []
        for qual in qualifications or []:
            q.append(
                PractitionerQualification(
                    code=CodeableConcept(
                        coding=[
                            Coding(
                                system="http://example.org/qualification",
                                code="qualification",
                                display="Qualification",
                            )
                        ]
                    ),
                    issuer={"reference": f"Organization/{str(qual)}"},
                )
            )

        return Practitioner(
            active=active if active is not None else self.fake.boolean(),
            name=[
                HumanName(
                    use=self.fake.random_element(
                        elements=(
                            "usual",
                            "official",
                            "temp",
                            "nickname",
                        )
                    ),
                    text=self.fake.name(),
                    family=self.fake.last_name(),
                    given=[self.fake.first_name()],
                )
            ],
            qualification=q if q is not None else None,
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

    def generate_healthcare_service(self, id: UUID, comment = None):
        return HealthcareService(
            id=Id(str(id)),
            comment=comment if comment else None,
        )

    def generate_practitioner_role(
        self,
        id: UUID,
        practitioner: str|None = None,
        organization: str|None = None,
        location: List[str]|None = None,
        healthcare_service: List[str]|None = None,
    ):
        return PractitionerRole(
            id=Id(str(id)),
            practitioner=Reference.construct(reference=f"Practitioner/{practitioner}") if practitioner else None,
            organization=Reference.construct(reference=f"Organization/{organization}") if organization else None,
            location=[Reference.construct(reference=f"Location/{loc}") for loc in location] if location else None,
            healthcareService=[Reference.construct(reference=f"HealthcareService/{hs}") for hs in healthcare_service] if healthcare_service else None,
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

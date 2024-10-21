import random
from typing import Optional, Literal, Union

import pytest
from faker import Faker

from app.params.endpoint_query_params import EndpointQueryParams
from app.params.organization_query_params import OrganizationQueryParams
from app.services.entity_services.endpoint_service import EndpointService
from app.services.entity_services.organization_service import OrganizationService
from app.services.matching_care_service import MatchingCareService
from utils import check_key_value, add_organization

fake = Faker("nl_nl")


@pytest.mark.parametrize(
    "active, ura_number, name, parent_organization, include, rev_include",
    [
        (True, 12345678, "Org A", None, None, None),
        (False, None, "Org B", True, "Organization.endpoint", None),
        (None, 87654321, None, None, None, "Location:organization"),
        (
            True,
            None,
            "Org C",
            True,
            None,
            "OrganizationAffiliation:primary-organization",
        ),
        (
            True,
            23456789,
            "Org D",
            False,
            "Organization.endpoint",
            "OrganizationAffiliation:participating-organization",
        ),
        (
            False,
            34567890,
            "Org E",
            True,
            None,
            "OrganizationAffiliation:primary-organization",
        ),
        (None, None, "Org F", None, None, "Location:organization"),
        (
            True,
            45678901,
            None,
            None,
            None,
            "OrganizationAffiliation:primary-organization",
        ),
        (
            False,
            56789012,
            "Org G",
            False,
            None,
            "OrganizationAffiliation:participating-organization",
        ),
        (True, None, None, True, None, "Location:organization"),
        (None, 67890123, "Org H", True, "Organization.endpoint", None),
        (
            False,
            78901234,
            "Org I",
            False,
            None,
            "OrganizationAffiliation:primary-organization",
        ),
        (True, 89012345, "Org J", None, None, "Location:organization"),
        (
            None,
            None,
            "Org K",
            False,
            None,
            "OrganizationAffiliation:primary-organization",
        ),
        (True, None, None, None, None, None),
    ],
)
def test_find_correct_organizations(
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    matching_care_service: MatchingCareService,
    active: Optional[bool],
    ura_number: Optional[int],
    name: Optional[str],
    parent_organization: Optional[bool],
    include: Optional[Literal["Organization.endpoint"]],
    rev_include: Union[
        Literal[
            "Location:organization",
            "OrganizationAffiliation:participating-organization",
            "OrganizationAffiliation:primary-organization",
        ]
    ],
) -> None:
    expected_org, expected_endpoint = add_organization(
        organization_service=organization_service,
        endpoint_service=endpoint_service,
        active=active,
        ura_number=ura_number,
        name=name,
        parent_organization=parent_organization,
        include=include,
    )

    query_params = OrganizationQueryParams(
        active=active,
        identifier=str(ura_number) if ura_number is not None else ura_number,
        name=name,
        partOf=expected_org.parent_organization_id,
        _include=include,
        _revInclude=rev_include,
    )

    result = matching_care_service.find_organizations(query_params)

    assert result is not None
    if active is not None:
        assert check_key_value(result, "active", active)
    if ura_number is not None:
        assert check_key_value(result, "value", str(ura_number))
    if name:
        assert check_key_value(result, "name", name)
    if include is not None:
        if expected_endpoint is None:
            raise AssertionError
        assert check_key_value(
            result, "reference", "Endpoint/" + str(expected_endpoint.id)
        )
    assert check_key_value(result, "value", str(expected_org.id))


def test_find_correct_endpoints(
    organization_service: OrganizationService,
    endpoint_service: EndpointService,
    matching_care_service: MatchingCareService,
) -> None:
    expected_org, expected_endpoint = add_organization(
        organization_service=organization_service,
        endpoint_service=endpoint_service,
        active=random.choice([True, False]),
        ura_number=fake.random_int(0, 99999999),
        name=fake.text(50),
        parent_organization=fake.boolean(50),
        include="Organization.endpoint",
    )

    if expected_endpoint is None:
        raise AssertionError

    endpoint_params = EndpointQueryParams(
        identifier=expected_endpoint.id,
        organization=expected_org.id,
    )

    endpoints = matching_care_service.find_endpoints(endpoint_params)

    assert endpoints is not None
    assert check_key_value(
        endpoints, "reference", "Organization/" + str(expected_org.ura_number)
    )
    assert check_key_value(endpoints, "value", str(expected_endpoint.id))
    assert check_key_value(endpoints, "address", expected_endpoint.address)

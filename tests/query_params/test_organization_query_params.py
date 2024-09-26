from typing import Any
from uuid import uuid4
from pydantic import ValidationError
import pytest

from app.params.organization_query_params import OrganizationQueryParams


@pytest.mark.parametrize(
    "correct_organization_params",
    [
        {
            "id": uuid4(),
            "active": True,
            "identifier": "some identifier",
            "partOf": uuid4(),
            "name": "Just a regular query parameter",
        },
        {
            "id": uuid4(),
            "active": True,
            "identifier": "some identifier",
            "name": "with only include parameter",
            "include": "Organization.endpoint",
        },
        {"name": "with only revInclude", "revInclude": "Location:organization"},
        {
            "name": "combination of include and revInclude",
            "include": "Organization.endpoint",
            "revInclude": "OrganizationAffiliation:participating-organization",
        },
        {
            "name": "with a variation of revInclude",
            "include": "Organization.endpoint",
            "revInclude": "OrganizationAffiliation:primary-organization",
        },
    ],
)
def test_correct_query_params_should_succeed(
    correct_organization_params: dict[str, Any]
) -> None:
    mock_model = OrganizationQueryParams(**correct_organization_params)

    expected_params = correct_organization_params
    actual_params = mock_model.model_dump(exclude_none=True)

    assert expected_params == actual_params


@pytest.mark.parametrize(
    "incorrect_organization_params",
    [
        {"id": uuid4(), "include": "Organization.incorrectJoin"},
        {"id": uuid4(), "include": "IncorrectResource:endpoint"},
        {"id": uuid4(), "revInclude": "Location:incorrectJoin"},
        {"id": uuid4(), "revInclude": "IncorrectResource:primary-organization"},
        {"id": uuid4(), "revInclude": "IncorrectResource:participating-organization"},
        {"id": uuid4(), "revInclude": "OrganizationAffiliation:incorrect-join"},
        {
            "id": uuid4(),
            "name": "use dot instead of column",
            "revInclude": "Location.organization",
        },
    ],
)
def test_incorrect_query_params_should_raise_value_error(
    incorrect_organization_params: dict[str, Any],
) -> None:
    with pytest.raises(ValueError):
        OrganizationQueryParams.model_validate(incorrect_organization_params)


@pytest.mark.parametrize(
    "incorrect_organization_params",
    [
        {"name": "Incorrect type", "id": 12345},
        {"name": "another incorrect type", "last_updated": ["some wrong data"]},
    ],
)
def test_incorrect_param_should_raise_validation_error(
    incorrect_organization_params: dict[str, Any]
) -> None:
    with pytest.raises(ValidationError):
        OrganizationQueryParams.model_validate(incorrect_organization_params)

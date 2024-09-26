from uuid import UUID

from pydantic import field_validator

from app.params.common_query_params import CommonQueryParams


class OrganizationQueryParams(CommonQueryParams):
    active: bool | None = None
    identifier: str | None = None
    name: str | None | None = None
    partOf: UUID | None = None
    type: str | None = None  # possible enum
    include: str | None = None
    revInclude: str | None = None

    @field_validator("include", check_fields=False)
    @classmethod
    def validate_include(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if value != "Organization.endpoint":
            raise ValueError(f"Unknown or incorrect resource {value}")

        return value

    @field_validator("revInclude", check_fields=False)
    @classmethod
    def validate_rev_include(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if ":" not in value:
            raise ValueError("Incorrect search query")

        data = value.split(":")
        resource = data[0]
        target = "".join(data[1:])

        if resource == "Location":
            if target == "organization":
                return value

        if resource == "OrganizationAffiliation":
            if (
                target == "participating-organization"
                or target == "primary-organization"
            ):
                return value

        raise ValueError(f"Unknown or incorrect resource {value}")

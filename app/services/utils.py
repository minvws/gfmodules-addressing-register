from datetime import datetime
from typing import Literal, Tuple, TypeVar
from uuid import UUID
from zoneinfo import ZoneInfo

from app.db.entities.mixin.common_mixin import CommonMixin

T = TypeVar("T", bound=CommonMixin)


def update_resource_meta(res: T, method: Literal["create", "update", "delete"]) -> T:
    res.version = res.version + 1 if method != "create" else 1
    if isinstance(res.data, dict):
        res.data.update(
            {
                "meta": {
                    "versionId": str(res.version),
                    "lastUpdated": datetime.now(ZoneInfo("UTC")).isoformat(),
                    "source": f"{res.__class__.__name__}/{res.fhir_id}",
                }
            }
        )

    if method == "create":
        request_method = "POST"
        response_status = "201 Created"
    elif method == "delete":
        request_method = "DELETE"
        response_status = "204 No Content"
        res.deleted = True
    else:  # update
        request_method = "PUT"
        response_status = "200 OK"

    res.bundle_meta = {
        "request": {
            "method": request_method,
            "url": f"{res.__class__.__name__}/{res.fhir_id}/_history/{res.version}",
        },
        "response": {"status": response_status, "etag": f'W/"{res.version}"'},
    }

    return res


def split_reference(reference: str) -> Tuple[str, UUID]:
    """
    Split a reference string into a tuple of (reference_type, reference_id). Will raise a ValueError when the ref_id
    is NOT a valid UUID

    Example:
        Organization/12345678-1234-5678-1234-567812345678 -> ("Organization", UUID("12345678-1234-5678-1234-567812345678"))

    """
    parts = reference.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid reference format {reference} (need: Type/UUID)")

    try:
        reference_type = str(parts[0])
        reference_id = UUID(parts[1])
    except ValueError:
        raise ValueError(f"Invalid reference format {reference} (needs: UUID)")

    return reference_type, reference_id

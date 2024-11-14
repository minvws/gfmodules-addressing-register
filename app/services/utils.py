from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo

from app.db.entities.endpoint.endpoint import Endpoint
from app.db.entities.organization.organization import Organization


def update_resource_meta(res: Organization|Endpoint, method: Literal["create", "update", "delete"]) -> None:
    res.version = res.version+1 if method != "create" else 1
    if isinstance(res.data, dict):
        res.data.update(
            {
                "meta": {
                    "versionId": res.version,
                    "lastUpdated": datetime.now(ZoneInfo("Europe/Paris")).isoformat(),
                    "source": f"https://example.org/{res.__class__.__name__}",
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


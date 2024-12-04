import json
from datetime import datetime, date
from typing import Optional, Dict, Any

from starlette.responses import Response

from app.db.entities.mixin.common_mixin import CommonMixin


def json_serial(obj: Any) -> str:
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


class FhirEntityResponse(Response):
    def __init__(self, entry: CommonMixin, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            content=json.dumps(entry.data, indent=2, default=json_serial),
            media_type="application/fhir+json",
            status_code=status_code,
            headers={
                "ETag": f"W/\"{entry.version}\"",
                "Last-Modified": entry.created_at.isoformat(),
                **(headers or {})
            }
       )

class FhirBundleResponse(Response):
    def __init__(self, bundle: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        super().__init__(
            content=json.dumps(bundle, indent=2, default=json_serial),
            media_type="application/fhir+json",
            status_code=status_code,
            headers=headers
        )

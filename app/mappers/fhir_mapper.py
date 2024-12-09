from enum import Enum
from typing import Sequence

from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.fhirtypes import Uri

from app.db.entities.mixin.common_mixin import CommonMixin
from app.exceptions.service_exceptions import ResourceNotFoundException


class BundleType(str, Enum):
    SEARCHSET = "searchset"
    HISTORY = "history"


def create_fhir_bundle(bundled_entries: list[BundleEntry], bundle_type: BundleType = BundleType.SEARCHSET) -> Bundle:
    return Bundle.construct(type=bundle_type, entry=bundled_entries, total=len(bundled_entries))


def create_bundle_entries(
    entries: Sequence[CommonMixin],
    with_req_resp: bool = False,
) -> list[BundleEntry]:
    listing = []
    for entry in entries:
        if entry.bundle_meta is None:
            raise ResourceNotFoundException(f"Entry {entry.fhir_id} bundle meta not found")

        params = {
            "fullUrl": Uri(f"{entry.fhir_id}/_history/{entry.version}"),
            "resource": entry.data,
        }
        if with_req_resp:
            params["request"] = entry.bundle_meta.get("request")
            params["response"] = entry.bundle_meta.get("response")

        listing.append(BundleEntry.construct(**params))  # type: ignore
    return listing

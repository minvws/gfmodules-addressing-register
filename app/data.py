from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ConnectionType(Enum):
    DicomWadoRs = "dicom-wado-rs"
    DicomQidoRs = "dicom-qido-rs"
    DicomStowRs = "dicom-stow-rs"
    DicomWadoUri = "dicom-wado-uri"
    Hl7FhirRest = "hl7-fhir-rest"
    Hl7FhirMsg = "hl7-fhir-msg"
    Hl7v2Mllp = "hl7v2-mllp"
    SecureEmail = "secure-email"
    DirectProject = "direct-project"
    CdsHooksService = "cds-hooks-service"

    def __str__(self) -> str:
        return self.value


class EndpointStatus(Enum):
    Active = "active"
    Suspended = "suspended"
    Error = "error"
    Off = "off"
    EnteredInError = "entered-in-error"

    @classmethod
    def from_str(cls, label: str) -> Optional["EndpointStatus"]:
        try:
            return cls(label.lower())
        except ValueError:
            return None

    def __str__(self) -> str:
        return self.value


@dataclass
class UraNumber:
    def __init__(self, value: Any) -> None:
        if (isinstance(value, int) or isinstance(value, str)) and len(str(value)) <= 8 and str(value).isdigit():
            self.value = str(value).zfill(8)
        else:
            raise ValueError("UraNumber must be 8 digits or less")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"UraNumber({self.value})"

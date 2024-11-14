import unittest

from unittest.mock import Mock, MagicMock

from fhir.resources.R4B.reference import Reference
from sqlalchemy.orm import Session

from app.db.entities.healthcare_service.healthcare_service import HealthcareServiceEntry
from app.db.entities.organization_affiliation.organization_affiliation import OrganizationAffiliationEntry
from app.services.reference_validator import ReferenceValidator

class TestReferenceValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = ReferenceValidator()
        self.session = Mock(spec=Session)


    def test_validate_reference_healthcare_service_valid(self) -> None:
        self.session.query.return_value.filter.return_value.first.return_value = HealthcareServiceEntry(fhir_id="123")

        data = Reference.construct(reference="HealthcareService/123")
        result = self.validator.validate_reference(self.session, data, ["HealthcareService"])

        self.assertTrue(result)
        self.session.query.assert_called_once_with(HealthcareServiceEntry)


    def test_validate_reference_organization_affiliation_invalid(self) -> None:
        self.session.query.return_value.filter.return_value.first.return_value = None

        data = Reference.construct(reference="OrganizationAffiliation/456")
        result = self.validator.validate_reference(self.session, data, ["OrganizationAffiliation"])

        self.assertFalse(result)
        self.session.query.assert_called_once_with(OrganizationAffiliationEntry)


    def test_validate_reference_invalid_reference_type(self) -> None:
        data = Reference.construct(reference="InvalidType/123")
        with self.assertRaises(ValueError):
            self.validator.validate_reference(self.session, data, ["HealthcareService"])


    def test_validate_list_mixed_references(self) -> None:
        self.session.query.return_value.filter.side_effect = [
            MagicMock(first=Mock(return_value=HealthcareServiceEntry(fhir_id="123"))),
            MagicMock(first=Mock(return_value=None))
        ]

        data = [
            Reference.construct(reference="HealthcareService/123"),
            Reference.construct(reference="HealthcareService/456"),
        ]

        result = self.validator.validate_list(self.session, data, ["HealthcareService"])

        self.assertFalse(result)
        self.assertEqual(self.session.query.call_count, 2)

    def test_validate_list_mixed_references_only_allow_single_type(self) -> None:
        self.session.query.return_value.filter.side_effect = [
            MagicMock(first=Mock(return_value=HealthcareServiceEntry(fhir_id="123"))),
        ]

        data = [
            Reference.construct(reference="HealthcareService/123"),
            Reference.construct(reference="OrganizationAffiliation/456"),
        ]

        with self.assertRaises(ValueError):
            self.validator.validate_list(self.session, data, ["HealthcareService"])

    def test_validate_list_mixed_references_allow_both_types(self) -> None:
        self.session.query.return_value.filter.side_effect = [
            MagicMock(first=Mock(return_value=HealthcareServiceEntry(fhir_id="123"))),
            MagicMock(first=Mock(return_value=OrganizationAffiliationEntry(fhir_id="456"))),
        ]

        data = [
            Reference.construct(reference="HealthcareService/123"),
            Reference.construct(reference="OrganizationAffiliation/456"),
        ]

        result = self.validator.validate_list(self.session, data, ["HealthcareService", "OrganizationAffiliation"])
        self.assertTrue(result)
        self.assertEqual(self.session.query.call_count, 2)

    def test_validate_list_mixed_references_all_allowed(self) -> None:
        self.session.query.return_value.filter.side_effect = [
            MagicMock(first=Mock(return_value=HealthcareServiceEntry(fhir_id="123"))),
            MagicMock(first=Mock(return_value=OrganizationAffiliationEntry(fhir_id="456"))),
        ]

        data = [
            Reference.construct(reference="HealthcareService/123"),
            Reference.construct(reference="OrganizationAffiliation/456"),
        ]

        result = self.validator.validate_list(self.session, data, [], all_allowed=True)
        self.assertTrue(result)
        self.assertEqual(self.session.query.call_count, 2)

import unittest

from app.data import ProviderID


class TestProviderId(unittest.TestCase):
    def test_provider_id(self) -> None:
        self.assertEqual("00001234", str(ProviderID("1234")))
        self.assertEqual("12345678", str(ProviderID("12345678")))

        with self.assertRaises(ValueError):
            ProviderID("1234567890")
        with self.assertRaises(ValueError):
            ProviderID("foobar")
        with self.assertRaises(ValueError):
            ProviderID("1A525")
        with self.assertRaises(ValueError):
            ProviderID("")

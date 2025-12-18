import json
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

# Adjust to your real module path
from core.views.getbookings import getbookings


def _parse_json(resp):
    return json.loads(resp.content.decode("utf-8"))


class GetBookingsPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_method_not_get_returns_400(self):
        req = self.rf.post("/api/bookings/someone@example.com/")
        resp = getbookings(req, customer_email="someone@example.com")

        self.assertEqual(resp.status_code, 400)
        payload = _parse_json(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "GET request required")

    def test_missing_customer_email_returns_400(self):
        req = self.rf.get("/api/bookings/")
        resp = getbookings(req, customer_email="")

        self.assertEqual(resp.status_code, 400)
        payload = _parse_json(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "customer_email query parameter is required")

    @patch("core.views.getbookings.service")  # patch the module-level instance
    def test_returns_bookings_serialized(self, service_mock: Mock):
        # Arrange: fake booking objects with the attributes your code reads
        b1 = SimpleNamespace(
            booking_id=1,
            product_id=10,
            customer_email="a@b.com",
            reseller_id=7,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 3),
            total_price=Decimal("99.90"),
        )
        b2 = SimpleNamespace(
            booking_id=2,
            product_id=11,
            customer_email="a@b.com",
            reseller_id=8,
            start_date=date(2025, 2, 10),
            end_date=date(2025, 2, 12),
            total_price=Decimal("50.00"),
        )
        service_mock.get_bookings.return_value = [b1, b2]

        # Act
        req = self.rf.get("/api/bookings/a@b.com/")
        resp = getbookings(req, customer_email="a@b.com")

        # Assert
        self.assertEqual(resp.status_code, 200)
        payload = _parse_json(resp)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], [
            {
                "booking_id": 1,
                "product_id": 10,
                "customer_email": "a@b.com",
                "reseller_id": 7,
                "start_date": "2025-01-01",
                "end_date": "2025-01-03",
                "total_price": "99.90",
            },
            {
                "booking_id": 2,
                "product_id": 11,
                "customer_email": "a@b.com",
                "reseller_id": 8,
                "start_date": "2025-02-10",
                "end_date": "2025-02-12",
                "total_price": "50.00",
            },
        ])

        service_mock.get_bookings.assert_called_once_with("a@b.com")

    @patch("core.views.getbookings.service")
    def test_json_decode_error_returns_400(self, service_mock: Mock):
        service_mock.get_bookings.side_effect = json.JSONDecodeError("msg", "doc", 0)

        req = self.rf.get("/api/bookings/a@b.com/")
        resp = getbookings(req, customer_email="a@b.com")

        self.assertEqual(resp.status_code, 400)
        payload = _parse_json(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "Invalid JSON")

    @patch("core.views.getbookings.service")
    def test_generic_exception_returns_400_and_message(self, service_mock: Mock):
        service_mock.get_bookings.side_effect = Exception("service down")

        req = self.rf.get("/api/bookings/a@b.com/")
        resp = getbookings(req, customer_email="a@b.com")

        self.assertEqual(resp.status_code, 400)
        payload = _parse_json(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "service down")

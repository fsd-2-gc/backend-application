import json
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

# Adjust if your module path is different
from core.views.getbooking import getbooking


def _parse(resp):
    return json.loads(resp.content.decode("utf-8"))


class GetBookingPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_method_not_get_returns_400(self):
        req = self.rf.post("/api/booking/1/")
        resp = getbooking(req, booking_id=1)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "GET request required")

    def test_missing_booking_id_returns_400(self):
        req = self.rf.get("/api/booking/")
        resp = getbooking(req, booking_id=0)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "booking_id query parameter is required")

    @patch("core.views.getbooking.service")
    def test_returns_booking_when_found(self, service_mock: Mock):
        # Fake booking object with required attributes
        booking = SimpleNamespace(
            booking_id=5,
            product_id=10,
            customer_email="user@example.com",
            reseller_id=3,
            start_date=date(2025, 3, 1),
            end_date=date(2025, 3, 5),
            total_price=Decimal("199.99"),
        )

        service_mock.get_booking.return_value = booking

        req = self.rf.get("/api/booking/5/")
        resp = getbooking(req, booking_id=5)

        self.assertEqual(resp.status_code, 200)
        payload = _parse(resp)

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], {
            "booking_id": 5,
            "product_id": 10,
            "customer_email": "user@example.com",
            "reseller_id": 3,
            "start_date": "2025-03-01",
            "end_date": "2025-03-05",
            "total_price": "199.99",
        })

        service_mock.get_booking.assert_called_once_with(5)

    @patch("core.views.getbooking.service")
    def test_json_decode_error_returns_400(self, service_mock: Mock):
        service_mock.get_booking.side_effect = json.JSONDecodeError(
            "msg", "doc", 0
        )

        req = self.rf.get("/api/booking/1/")
        resp = getbooking(req, booking_id=1)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "Invalid JSON")

        service_mock.get_booking.assert_called_once_with(1)

    @patch("core.views.getbooking.service")
    def test_generic_exception_returns_400_and_message(self, service_mock: Mock):
        service_mock.get_booking.side_effect = Exception("booking not found")

        req = self.rf.get("/api/booking/99/")
        resp = getbooking(req, booking_id=99)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "booking not found")

        service_mock.get_booking.assert_called_once_with(99)

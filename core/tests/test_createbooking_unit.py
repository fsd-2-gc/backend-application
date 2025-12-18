import json
from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

# Adjust to your real module path
from core.views.createbooking import createbooking


def _parse(resp):
    return json.loads(resp.content.decode("utf-8"))


class CreateBookingPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_method_not_post_returns_400(self):
        req = self.rf.get("/api/bookings/")
        resp = createbooking(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "POST request required")

    @patch("core.views.createbooking.send_confirmation_mail")
    @patch("core.views.createbooking.Reseller")
    @patch("core.views.createbooking.Product")
    @patch("core.views.createbooking.service")
    def test_happy_path_creates_booking_and_sends_mail(
        self,
        service_mock: Mock,
        ProductMock: Mock,
        ResellerMock: Mock,
        send_mail_mock: Mock,
    ):
        # Arrange: booking returned by service
        booking = SimpleNamespace(
            booking_id=77,
            product_id=10,
            reseller_id=5,
            customer_email="user@example.com",
            start_date=datetime(2025, 1, 1, 10, 0),
            end_date=datetime(2025, 1, 2, 12, 30),
            total_price=Decimal("99.90"),
        )
        service_mock.create_booking.return_value = booking

        # Arrange: product & reseller lookups
        ProductMock.objects.get.return_value = SimpleNamespace(type="bike")
        reseller_obj = SimpleNamespace(name="Best Reseller")
        ResellerMock.objects.filter.return_value.first.return_value = reseller_obj

        body = {
            "product_id": "10",
            "customer_email": "user@example.com",
            "reseller_id": "5",
            "start_date": "2025-01-01T10:00:00",
            "end_date": "2025-01-02T12:30:00",
            "total_price": "99.90",
        }

        req = self.rf.post(
            "/api/bookings/",
            data=json.dumps(body),
            content_type="application/json",
        )

        # Act
        resp = createbooking(req)

        # Assert response
        self.assertEqual(resp.status_code, 201)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], {"booking_id": 77})

        # Assert service called with DTO-like object with expected parsed types/values
        service_mock.create_booking.assert_called_once()
        dto_arg = service_mock.create_booking.call_args[0][0]

        self.assertEqual(dto_arg.product_id, 10)
        self.assertEqual(dto_arg.customer_email, "user@example.com")
        self.assertEqual(dto_arg.reseller_id, 5)
        self.assertEqual(dto_arg.start_date, datetime.fromisoformat("2025-01-01T10:00:00"))
        self.assertEqual(dto_arg.end_date, datetime.fromisoformat("2025-01-02T12:30:00"))
        self.assertEqual(dto_arg.total_price, Decimal("99.90"))

        # Assert DB lookups invoked correctly (but mocked)
        ProductMock.objects.get.assert_called_once_with(pk=10)
        ResellerMock.objects.filter.assert_called_once_with(pk=5)
        ResellerMock.objects.filter.return_value.first.assert_called_once_with()

        # Assert mail sent with expected fields
        send_mail_mock.assert_called_once()
        to_email, mail_ctx = send_mail_mock.call_args[0]

        self.assertEqual(to_email, "user@example.com")
        self.assertEqual(mail_ctx["subject"], "Your booking is confirmed")
        self.assertEqual(mail_ctx["email"], "user@example.com")
        self.assertEqual(mail_ctx["booking_id"], 77)
        self.assertEqual(mail_ctx["reseller_name"], "Best Reseller")
        self.assertEqual(mail_ctx["start_date"], "2025-01-01 10:00")
        self.assertEqual(mail_ctx["end_date"], "2025-01-02 12:30")
        self.assertEqual(mail_ctx["parking_type"], "bike")
        self.assertIn("CURRENT_YEAR", mail_ctx)

    @patch("core.views.createbooking.send_confirmation_mail")
    @patch("core.views.createbooking.Reseller")
    @patch("core.views.createbooking.Product")
    @patch("core.views.createbooking.service")
    def test_reseller_missing_sets_empty_name(
        self,
        service_mock: Mock,
        ProductMock: Mock,
        ResellerMock: Mock,
        send_mail_mock: Mock,
    ):
        booking = SimpleNamespace(
            booking_id=1,
            product_id=1,
            reseller_id=999,
            customer_email="x@y.com",
            start_date=datetime(2025, 1, 1, 9, 0),
            end_date=datetime(2025, 1, 1, 10, 0),
            total_price=Decimal("10.00"),
        )
        service_mock.create_booking.return_value = booking
        ProductMock.objects.get.return_value = SimpleNamespace(type="scooter")
        ResellerMock.objects.filter.return_value.first.return_value = None  # reseller not found

        body = {
            "product_id": "1",
            "customer_email": "x@y.com",
            "reseller_id": "999",
            "start_date": "2025-01-01T09:00:00",
            "end_date": "2025-01-01T10:00:00",
            "total_price": "10.00",
        }
        req = self.rf.post("/api/bookings/", data=json.dumps(body), content_type="application/json")
        resp = createbooking(req)

        self.assertEqual(resp.status_code, 201)

        _, mail_ctx = send_mail_mock.call_args[0]
        self.assertEqual(mail_ctx["reseller_name"], "")

    def test_invalid_json_returns_400(self):
        req = self.rf.post("/api/bookings/", data="{bad json", content_type="application/json")
        resp = createbooking(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "Invalid JSON")

    @patch("core.views.createbooking.service")
    def test_service_exception_returns_400_and_message(self, service_mock: Mock):
        service_mock.create_booking.side_effect = Exception("service down")

        body = {
            "product_id": "10",
            "customer_email": "user@example.com",
            "reseller_id": "5",
            "start_date": "2025-01-01T10:00:00",
            "end_date": "2025-01-02T12:30:00",
            "total_price": "99.90",
        }
        req = self.rf.post("/api/bookings/", data=json.dumps(body), content_type="application/json")
        resp = createbooking(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "service down")

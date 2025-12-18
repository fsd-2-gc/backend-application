import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

# Adjust to your real module path
from core.views.cancelbooking import cancelbooking


def _parse(resp):
    return json.loads(resp.content.decode("utf-8"))


class CancelBookingPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_method_not_post_returns_400(self):
        req = self.rf.get("/api/bookings/1/cancel/")
        resp = cancelbooking(req, booking_id=1)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "POST request required")

    @patch("core.views.cancelbooking.send_cancellation_mail")
    @patch("core.views.cancelbooking.Reseller")
    @patch("core.views.cancelbooking.service")
    def test_happy_path_returns_200_and_sends_email(
        self,
        service_mock: Mock,
        ResellerMock: Mock,
        send_mail_mock: Mock,
    ):
        booking = SimpleNamespace(
            booking_id=10,
            reseller_id=5,
            customer_email="user@example.com",
            status="cancelled",
        )
        service_mock.cancel_booking.return_value = booking

        reseller = SimpleNamespace(name="Reseller A")
        ResellerMock.objects.filter.return_value.first.return_value = reseller

        req = self.rf.post("/api/bookings/10/cancel/")
        resp = cancelbooking(req, booking_id=10)

        self.assertEqual(resp.status_code, 200)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], {"booking_id": 10, "status": "cancelled"})

        service_mock.cancel_booking.assert_called_once_with(10)
        ResellerMock.objects.filter.assert_called_once_with(pk=5)
        ResellerMock.objects.filter.return_value.first.assert_called_once_with()

        send_mail_mock.assert_called_once()
        to_email, template = send_mail_mock.call_args[0]
        self.assertEqual(to_email, "user@example.com")
        self.assertEqual(template["subject"], "Your booking has been cancelled")
        self.assertEqual(template["customer_email"], "user@example.com")
        self.assertEqual(template["booking_id"], 10)
        self.assertEqual(template["reseller_name"], "Reseller A")
        self.assertIn("CURRENT_YEAR", template)

    @patch("core.views.cancelbooking.send_cancellation_mail")
    @patch("core.views.cancelbooking.Reseller")
    @patch("core.views.cancelbooking.service")
    def test_reseller_missing_sets_empty_reseller_name(
        self,
        service_mock: Mock,
        ResellerMock: Mock,
        send_mail_mock: Mock,
    ):
        booking = SimpleNamespace(
            booking_id=11,
            reseller_id=999,
            customer_email="user@example.com",
            status="cancelled",
        )
        service_mock.cancel_booking.return_value = booking

        ResellerMock.objects.filter.return_value.first.return_value = None

        req = self.rf.post("/api/bookings/11/cancel/")
        resp = cancelbooking(req, booking_id=11)

        self.assertEqual(resp.status_code, 200)

        _, template = send_mail_mock.call_args[0]
        self.assertEqual(template["reseller_name"], "")

    @patch("core.views.cancelbooking.send_cancellation_mail")
    @patch("core.views.cancelbooking.Reseller")
    @patch("core.views.cancelbooking.service")
    def test_email_errors_are_swallowed_still_returns_200(
        self,
        service_mock: Mock,
        ResellerMock: Mock,
        send_mail_mock: Mock,
    ):
        booking = SimpleNamespace(
            booking_id=12,
            reseller_id=5,
            customer_email="user@example.com",
            status="cancelled",
        )
        service_mock.cancel_booking.return_value = booking

        # Force email send to fail
        send_mail_mock.side_effect = Exception("smtp down")

        req = self.rf.post("/api/bookings/12/cancel/")
        resp = cancelbooking(req, booking_id=12)

        self.assertEqual(resp.status_code, 200)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"]["booking_id"], 12)
        self.assertEqual(payload["data"]["status"], "cancelled")

    @patch("core.views.cancelbooking.service")
    def test_value_error_returns_404(self, service_mock: Mock):
        service_mock.cancel_booking.side_effect = ValueError("Booking not found")

        req = self.rf.post("/api/bookings/404/cancel/")
        resp = cancelbooking(req, booking_id=404)

        self.assertEqual(resp.status_code, 404)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "Booking not found")

    @patch("core.views.cancelbooking.service")
    def test_generic_exception_returns_400(self, service_mock: Mock):
        service_mock.cancel_booking.side_effect = Exception("boom")

        req = self.rf.post("/api/bookings/1/cancel/")
        resp = cancelbooking(req, booking_id=1)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "boom")

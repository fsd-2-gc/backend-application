import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

# Adjust this import to your real module path
from core.views.createproduct import createproduct


def _parse(resp):
    return json.loads(resp.content.decode("utf-8"))


class CreateProductPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_method_not_post_returns_400(self):
        req = self.rf.get("/api/products/")
        resp = createproduct(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "POST request required")

    @patch("core.views.createproduct.Product")
    def test_creates_product_and_returns_201_with_product_id(self, ProductMock):
        # Arrange
        created = SimpleNamespace(product_id=123)
        ProductMock.objects.create.return_value = created

        body = {
            "reseller_id": 7,
            "name": "My Product",
            "type": "bike",
            "price_per_day": "10.50",
            "rating": "4.2",
        }

        req = self.rf.post(
            "/api/products/",
            data=json.dumps(body),
            content_type="application/json",
        )

        # Act
        resp = createproduct(req)

        # Assert
        self.assertEqual(resp.status_code, 201)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], {"product_id": 123})

        ProductMock.objects.create.assert_called_once_with(
            reseller_id=7,
            name="My Product",
            type="bike",
            price_per_day="10.50",
            rating="4.2",
        )

    @patch("core.views.createproduct.Product")
    def test_missing_fields_still_calls_create_with_none(self, ProductMock):
        # Arrange
        created = SimpleNamespace(product_id=1)
        ProductMock.objects.create.return_value = created

        body = {
            "reseller_id": 5,
            # name/type/price_per_day/rating omitted on purpose
        }

        req = self.rf.post(
            "/api/products/",
            data=json.dumps(body),
            content_type="application/json",
        )

        # Act
        resp = createproduct(req)

        # Assert
        self.assertEqual(resp.status_code, 201)
        ProductMock.objects.create.assert_called_once_with(
            reseller_id=5,
            name=None,
            type=None,
            price_per_day=None,
            rating=None,
        )

    @patch("core.views.createproduct.Product")
    def test_invalid_json_returns_400(self, ProductMock):
        # Invalid JSON body
        req = self.rf.post(
            "/api/products/",
            data="{not valid json",
            content_type="application/json",
        )

        resp = createproduct(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        # message text can vary by Python/json, just assert it's non-empty
        self.assertTrue(isinstance(payload["data"], str))
        self.assertTrue(len(payload["data"]) > 0)

        ProductMock.objects.create.assert_not_called()

    @patch("core.views.createproduct.Product")
    def test_orm_exception_returns_400_and_message(self, ProductMock):
        ProductMock.objects.create.side_effect = Exception("db down")

        body = {
            "reseller_id": 7,
            "name": "My Product",
            "type": "bike",
            "price_per_day": "10.50",
            "rating": "4.2",
        }
        req = self.rf.post(
            "/api/products/",
            data=json.dumps(body),
            content_type="application/json",
        )

        resp = createproduct(req)

        self.assertEqual(resp.status_code, 400)
        payload = _parse(resp)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "db down")

        ProductMock.objects.create.assert_called_once()

import json
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, RequestFactory

from core.views.getproduct import getproduct


class GetProductPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    @patch("core.views.getproduct.Product")
    def test_returns_product_when_found(self, ProductMock):
        # Arrange
        product_dict = {
            "product_id": 10,
            "reseller_id": 3,
            "name": "Test Product",
            "type": "bike",
            "price_per_day": "12.50",
            "rating": "4.2",
        }

        qs = Mock(name="qs")
        values_qs = Mock(name="values_qs")
        values_qs.first.return_value = product_dict
        qs.values.return_value = values_qs
        ProductMock.objects.filter.return_value = qs

        # Act
        req = self.rf.get("/api/products/10/")
        resp = getproduct(req, product_id=10)

        # Assert
        self.assertEqual(resp.status_code, 200)
        payload = json.loads(resp.content.decode("utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"], product_dict)

        ProductMock.objects.filter.assert_called_once_with(product_id=10)
        qs.values.assert_called_once_with(
            "product_id",
            "reseller_id",
            "name",
            "type",
            "price_per_day",
            "rating",
        )
        values_qs.first.assert_called_once_with()

    @patch("core.views.getproduct.Product")
    def test_returns_404_when_not_found(self, ProductMock):
        # Arrange: .first() returns None -> not found
        qs = Mock(name="qs")
        values_qs = Mock(name="values_qs")
        values_qs.first.return_value = None
        qs.values.return_value = values_qs
        ProductMock.objects.filter.return_value = qs

        # Act
        req = self.rf.get("/api/products/999/")
        resp = getproduct(req, product_id=999)

        # Assert
        self.assertEqual(resp.status_code, 404)
        payload = json.loads(resp.content.decode("utf-8"))

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "Product not found")

        ProductMock.objects.filter.assert_called_once_with(product_id=999)
        values_qs.first.assert_called_once_with()

    @patch("core.views.getproduct.Product")
    def test_returns_500_on_exception(self, ProductMock):
        # Arrange: make ORM call raise
        ProductMock.objects.filter.side_effect = Exception("boom")

        # Act
        req = self.rf.get("/api/products/1/")
        resp = getproduct(req, product_id=1)

        # Assert
        self.assertEqual(resp.status_code, 500)
        payload = json.loads(resp.content.decode("utf-8"))

        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["data"], "boom")

        ProductMock.objects.filter.assert_called_once_with(product_id=1)

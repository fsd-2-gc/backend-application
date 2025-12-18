import json
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch

from django.test import SimpleTestCase, RequestFactory

from core.views.getproducts import getproducts


def _make_qs(items=None, total=0):
    """
    Build a mock queryset chain that supports:
      Product.objects.all().filter(...).count()
      qs.values(...)[start:end]
    """
    if items is None:
        items = []

    qs = Mock(name="qs")
    qs.count.return_value = total

    # MagicMock so slicing (__getitem__) works
    values_qs = MagicMock(name="values_qs")
    qs.values.return_value = values_qs

    # qs.values(...)[start:end] returns items
    values_qs.__getitem__.return_value = items

    return qs, values_qs


class GetProductsPureUnitTests(SimpleTestCase):
    def setUp(self):
        self.rf = RequestFactory()

    @patch("core.views.getproducts.Product")
    def test_defaults_page_1_and_min_rating_0(self, ProductMock):
        qs, values_qs = _make_qs(items=[{"product_id": 1}], total=123)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)

        payload = json.loads(resp.content.decode("utf-8"))

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["data"]["total"], 123)
        self.assertEqual(payload["data"]["items"], [{"product_id": 1}])

        ProductMock.objects.all.assert_called_once_with()
        ProductMock.objects.all.return_value.filter.assert_called_once_with(
            rating__gte=Decimal("0")
        )

        # page=1 => slice [0:25]
        values_qs.__getitem__.assert_called_once_with(slice(0, 25))

    @patch("core.views.getproducts.Product")
    def test_page_non_int_defaults_to_1(self, ProductMock):
        qs, values_qs = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?page=abc")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        values_qs.__getitem__.assert_called_once_with(slice(0, 25))

    @patch("core.views.getproducts.Product")
    def test_page_less_than_1_clamps_to_1(self, ProductMock):
        qs, values_qs = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?page=0")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        values_qs.__getitem__.assert_called_once_with(slice(0, 25))

    @patch("core.views.getproducts.Product")
    def test_page_2_slices_25_to_50(self, ProductMock):
        qs, values_qs = _make_qs(items=[{"product_id": 26}], total=60)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?page=2")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        values_qs.__getitem__.assert_called_once_with(slice(25, 50))

    @patch("core.views.getproducts.Product")
    def test_min_rating_valid_decimal(self, ProductMock):
        qs, _ = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?min_rating=4.2")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        ProductMock.objects.all.return_value.filter.assert_called_once_with(
            rating__gte=Decimal("4.2")
        )

    @patch("core.views.getproducts.Product")
    def test_min_rating_invalid_defaults_to_0(self, ProductMock):
        qs, _ = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?min_rating=not-a-number")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        ProductMock.objects.all.return_value.filter.assert_called_once_with(
            rating__gte=Decimal("0")
        )

    @patch("core.views.getproducts.Product")
    def test_min_rating_negative_clamps_to_0(self, ProductMock):
        qs, _ = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?min_rating=-1")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        ProductMock.objects.all.return_value.filter.assert_called_once_with(
            rating__gte=Decimal("0")
        )

    @patch("core.views.getproducts.Product")
    def test_min_rating_above_5_clamps_to_5(self, ProductMock):
        qs, _ = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/?min_rating=999")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)
        ProductMock.objects.all.return_value.filter.assert_called_once_with(
            rating__gte=Decimal("5")
        )

    @patch("core.views.getproducts.Product")
    def test_values_fields_are_exact(self, ProductMock):
        qs, _ = _make_qs(items=[], total=0)
        ProductMock.objects.all.return_value.filter.return_value = qs

        req = self.rf.get("/api/products/")
        resp = getproducts(req)

        self.assertEqual(resp.status_code, 200)

        qs.values.assert_called_once_with(
            "product_id",
            "reseller_id",
            "name",
            "type",
            "price_per_day",
            "rating",
        )

from django.http import JsonResponse
from ..models import Product
from decimal import Decimal, InvalidOperation


def getproducts(request):
    page_size = 25
    page_str = request.GET.get("page", "1")
    min_rating_str = request.GET.get("min_rating", "0")
    try:
        page = int(page_str)
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        page = 1

    # Parse and clamp min_rating to [0, 5]
    try:
        min_rating = Decimal(min_rating_str)
    except (TypeError, InvalidOperation):
        min_rating = Decimal("0")

    if min_rating < 0:
        min_rating = Decimal("0")
    if min_rating > 5:
        min_rating = Decimal("5")

    qs = Product.objects.all().filter(rating__gte=min_rating)
    total = qs.count()

    start = (page - 1) * page_size
    end = start + page_size

    products = qs.values(
        'product_id',
        'reseller_id',
        'name',
        'type',
        'price_per_day',
        'rating'
    )[start:end]

    return JsonResponse({
        "status": "ok",
        "data": {
            "total": total,
            "items": list(products)
        }
    }, status=200)

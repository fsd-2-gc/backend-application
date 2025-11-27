from django.http import JsonResponse
from ..models import Product


def getproducts(request):
    page_size = 25
    page_str = request.GET.get("page", "1")
    try:
        page = int(page_str)
        if page < 1:
            page = 1
    except (TypeError, ValueError):
        page = 1

    qs = Product.objects.all()
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

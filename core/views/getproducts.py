from django.http import JsonResponse
from ..models import Product

def getproducts(request):
    products = Product.objects.all().values(
        'product_id',
        'reseller_id',
        'name',
        'type',
        'price_per_day',
        'rating'
    )
    # Convert queryset to list for JSON serialization
    product_list = list(products)

    return JsonResponse({
        "status": "ok",
        "data": product_list
    }, status=200)

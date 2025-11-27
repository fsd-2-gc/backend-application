from django.http import JsonResponse
from core.models import Product
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def getproduct(request, product_id):
    try:
        product = Product.objects.filter(product_id=product_id).values(
            'product_id',
            'reseller_id',
            'name',
            'type',
            'price_per_day',
            'rating'
        ).first()

        if not product:
            return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

        return JsonResponse({
            "status": "ok",
            "data": product
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

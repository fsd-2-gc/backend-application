from django.http import JsonResponse
import json
from core.models import Product


def createproduct(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    try:
        data = json.loads(request.body)

        # Support both old and new payload keys for backward compatibility
        reseller_id = data.get("reseller_id")

        product = Product.objects.create(
            reseller_id=reseller_id,
            name=data.get("name"),
            type=data.get("type"),
            price_per_day=data.get("price_per_day"),
            rating=data.get("rating"),
        )

        return JsonResponse({
            "status": "created",
            "product_id": product.product_id
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

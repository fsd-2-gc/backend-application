from django.http import JsonResponse
import json
from datetime import datetime
from decimal import Decimal
from core.dto.booking_dto import BookingDTO
from core.service.booking_service import BookingService

service = BookingService()


def createbooking(request):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "data": "POST request required"
        }, status=400)

    try:
        data = json.loads(request.body)

        dto = BookingDTO(
            product_id=int(data.get("product_id")),
            customer_email=str(data.get("customer_email")),
            reseller_id=int(data.get("reseller_id")),
            start_date=datetime.fromisoformat(data.get("start_date")),
            end_date=datetime.fromisoformat(data.get("end_date")),
            total_price=Decimal(str(data.get("total_price")))
        )

        booking = service.create_booking(dto)

        return JsonResponse({
            "status": "ok",
            "data": {
                "booking_id": booking.booking_id
            }
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "data": "Invalid JSON"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "data": str(e)
        }, status=400)

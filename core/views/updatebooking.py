from django.http import JsonResponse
import json
from datetime import datetime
from decimal import Decimal
from core.dto.booking_dto import BookingDTO
from core.models import Booking
from core.service.booking_service import BookingService

service = BookingService()


def updatebooking(request, booking_id):
    if request.method != "PUT":
        return JsonResponse({
            "status": "error",
            "data": "PUT request required"
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

        booking = service.update_booking(booking_id, dto)

        return JsonResponse({
            "status": "ok",
            "data": {
                "booking_id": booking.booking_id
            }
        }, status=200)

    except Booking.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "data": "Booking not found"
        }, status=404)

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

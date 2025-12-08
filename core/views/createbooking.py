from django.http import JsonResponse
import json
from datetime import datetime
from decimal import Decimal
from core.dto.booking_dto import BookingDTO
from core.service.booking_service import BookingService
from core.models import Product, Reseller
from utilities.mailerutility import send_confirmation_mail

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

        product = Product.objects.get(pk=booking.product_id)
        reseller = Reseller.objects.filter(pk=booking.reseller_id).first()
        reseller_name = reseller.name if reseller else ""
        send_confirmation_mail(booking.customer_email, {
            "subject": "Your booking is confirmed",
            "email": booking.customer_email,
            "booking_id": booking.booking_id,
            "reseller_name": reseller_name,
            "start_date": booking.start_date.strftime('%Y-%m-%d %H:%M'),
            "end_date": booking.end_date.strftime('%Y-%m-%d %H:%M'),
            "parking_type": getattr(product, 'type', ''),
            "CURRENT_YEAR": datetime.now().year,
        })

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

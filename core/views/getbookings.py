from django.http import JsonResponse
import json
from core.service.booking_service import BookingService

service = BookingService()


def getbookings(request, customer_email: str):
    if request.method != "GET":
        return JsonResponse({
            "status": "error",
            "data": "GET request required"
        }, status=400)

    try:
        if not customer_email:
            return JsonResponse({
                "status": "error",
                "data": "customer_email query parameter is required"
            }, status=400)

        bookings = service.get_bookings(customer_email)

        response = []
        for booking in bookings:
            response.append({
                "booking_id": booking.booking_id,
                "product_id": booking.product_id,
                "customer_email": booking.customer_email,
                "reseller_id": booking.reseller_id,
                "start_date": booking.start_date.isoformat(),
                "end_date": booking.end_date.isoformat(),
                "total_price": str(booking.total_price),
        })

        return JsonResponse({
            "status": "ok",
            "data": response
        }, status=200)

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

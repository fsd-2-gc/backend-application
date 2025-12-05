from django.http import JsonResponse
from core.service.booking_service import BookingService

service = BookingService()


def cancelbooking(request, booking_id: int):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "data": "POST request required"
        }, status=400)

    try:
        booking = service.cancel_booking(booking_id)
        return JsonResponse({
            "status": "ok",
            "data": {
                "booking_id": booking.booking_id,
                "status": booking.status
            }
        }, status=200)
    except ValueError as e:
        # Booking not found
        return JsonResponse({
            "status": "error",
            "data": str(e)
        }, status=404)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "data": str(e)
        }, status=400)

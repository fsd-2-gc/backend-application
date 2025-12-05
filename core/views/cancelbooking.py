from django.http import JsonResponse
from core.service.booking_service import BookingService
from core.models import Reseller
from utilities.mailerutility import send_cancellation_mail
from datetime import datetime

service = BookingService()


def cancelbooking(request, booking_id: int):
    if request.method != "POST":
        return JsonResponse({
            "status": "error",
            "data": "POST request required"
        }, status=400)

    try:
        booking = service.cancel_booking(booking_id)
        # Attempt to send cancellation email (non-blocking)
        try:
            reseller = Reseller.objects.filter(pk=booking.reseller_id).first()
            reseller_name = reseller.name if reseller else ""

            template_model = {
                "subject": "Your booking has been cancelled",
                "customer_email": booking.customer_email,
                "booking_id": booking.booking_id,
                "reseller_name": reseller_name,
                "CURRENT_YEAR": datetime.now().year,
            }
            send_cancellation_mail(booking.customer_email, template_model)
        except Exception:
            # Swallow any email errors; they should not impact API response
            pass
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

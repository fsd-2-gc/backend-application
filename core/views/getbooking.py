from django.views import View
from django.http import JsonResponse, HttpResponseNotAllowed
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from decimal import Decimal
from core.dto.booking_dto import BookingDTO
from core.service.booking_service import BookingService

service = BookingService()

@method_decorator(csrf_exempt, name='dispatch')
class getbookings(View):
    def get(self, request):
        if not booking_id:
            return JsonResponse({'error': 'booking_id parameter is required'}, status=400)

        try:
            booking = BookingService.get_booking(booking_id)
            if not booking:
                return JsonResponse({'error': 'Booking not found'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid booking_id'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        response = {
            'booking_id': booking.booking_id,
            'product_id': booking.product_id,
            'customer_email': booking.customer_email,
            'reseller_id': booking.reseller_id,
            'start_date': booking.start_date.isoformat(),
            'end_date': booking.end_date.isoformat(),
            'total_price': str(booking.total_price),
            'status': booking.status
        }

        return JsonResponse(response, status=200)




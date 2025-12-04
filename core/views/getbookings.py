from django.views import View
from django.http import JsonResponse
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
        email = request.GET.get('email')
        if not email:
            return JsonResponse({'error': 'Email parameter is required'}, status=400)

        try:
            bookings = BookingService.get_bookings(email)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        response = [
            {
                'booking_id': booking.booking_id,
                'product_id': booking.product_id,
                'customer_email': booking.customer_email,
                'reseller_id': booking.reseller_id,
                'start_date': booking.start_date.isoformat(),
                'end_date': booking.end_date.isoformat(),
                'total_price': str(booking.total_price),
                'status': booking.status
            }
            for booking in bookings
        ]

        return JsonResponse(response, safe=False, status=200)
        












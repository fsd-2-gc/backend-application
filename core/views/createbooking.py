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
class BookingCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        required_fields = ['product_id', 'customer_email', 'reseller_id', 'start_date', 'end_date', 'total_price']
        for field in required_fields:
            if field not in data:
                return JsonResponse({'error': f'Missing field: {field}'}, status=400)

        try:
            dto = BookingDTO(
                product_id=int(data['product_id']),
                customer_email=str(data['customer_email']),
                reseller_id=int(data['reseller_id']),
                start_date=datetime.fromisoformat(data['start_date']),
                end_date=datetime.fromisoformat(data['end_date']),
                total_price=Decimal(str(data['total_price']))
            )
        except Exception as e:
            return JsonResponse({'error': 'Invalid field format', 'detail': str(e)}, status=400)

        try:
            booking = service.create_booking(dto)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': 'Server error while creating booking', 'detail': str(e)}, status=500)

        return JsonResponse({
            'booking_id': booking.booking_id,
            'product_id': booking.product_id,
            'customer_email': booking.customer_email,
            'reseller_id': booking.reseller_id,
            'start_date': booking.start_date.isoformat(),
            'end_date': booking.end_date.isoformat(),
            'total_price': str(booking.total_price),
            'status': booking.status,
            'access_token': booking.access_token
        }, status=201)

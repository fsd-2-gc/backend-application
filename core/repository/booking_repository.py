from core.models import Booking, Status
from core.dto.booking_dto import BookingDTO

class BookingRepository:
    @staticmethod
    def create_booking(dto: BookingDTO):
        booking = Booking.objects.create(
            product_id=dto.product_id,
            customer_email=dto.customer_email,
            reseller_id=dto.reseller_id,
            start_date=dto.start_date,
            end_date=dto.end_date,
            total_price=dto.total_price,
            status=Status.Pending.value
        )
        return booking
    
    @staticmethod
    def get_bookings():
        bookings = Booking.objects.get(
            #fill DAL logic
        )

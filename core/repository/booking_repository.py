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
    def get_bookings(email: str):
        try:
            return Booking.objects.filter(customer_email = email)
        except Booking.DoesNotExist:
            raise ValueError("Bookings not found")

    @staticmethod
    def cancel_booking(booking_id: int) -> Booking:
        try:
            booking = Booking.objects.get(pk=booking_id)
        except Booking.DoesNotExist:
            raise ValueError("Booking not found")

        if booking.status == Status.Cancelled.value:
            return booking

        booking.status = Status.Cancelled.value
        booking.save()
        return booking

from core.repository.booking_repository import BookingRepository
from core.dto.booking_dto import BookingDTO

class BookingService:
    @staticmethod
    def create_booking(dto: BookingDTO):
        return BookingRepository.create_booking(dto)

    @staticmethod
    def get_bookings(user_email):
        return BookingRepository.get_bookings(user_email)
    
    @staticmethod
    def get_booking(booking_id):
        return BookingRepository.get_booking(booking_id)
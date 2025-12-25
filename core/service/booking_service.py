from core.repository.booking_repository import BookingRepository
from core.dto.booking_dto import BookingDTO

class BookingService:
    @staticmethod
    def create_booking(dto: BookingDTO):
        return BookingRepository.create_booking(dto)

    @staticmethod
    def get_bookings(email: str):
        return BookingRepository.get_bookings(email)

    @staticmethod
    def get_booking(booking_id: int):
        return BookingRepository.get_booking(booking_id)

    @staticmethod
    def cancel_booking(booking_id: int):
        return BookingRepository.cancel_booking(booking_id)

    @staticmethod
    def update_booking(booking_id: int, dto: BookingDTO):
        return BookingRepository.update_booking(booking_id, dto)
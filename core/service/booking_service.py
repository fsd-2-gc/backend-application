from core.repository.booking_repository import BookingRepository
from core.dto.booking_dto import BookingDTO

class BookingService:
    @staticmethod
    def create_booking(dto: BookingDTO):
        return BookingRepository.create_booking(dto)

    @staticmethod
    def cancel_booking(booking_id: int):
        return BookingRepository.cancel_booking(booking_id)

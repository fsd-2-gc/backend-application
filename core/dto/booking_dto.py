from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class BookingDTO:
    product_id: int
    customer_email: str
    reseller_id: int
    start_date: date
    end_date: date
    total_price: Decimal

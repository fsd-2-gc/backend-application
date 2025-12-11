from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class BookingDTO:
    product_id: int
    customer_email: str
    reseller_id: int
    start_date: datetime
    end_date: datetime
    total_price: Decimal

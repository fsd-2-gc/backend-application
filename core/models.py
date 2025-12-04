from django.db import models
from enum import Enum
import secrets

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    company_id = models.IntegerField()
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=50)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.name

class Status(Enum):
    Pending = 0
    Confirmed = 1
    Cancelled = 2
    Refunded = 3

Status_Choices = [(status.value, status.name) for status in Status]

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    product_id = models.IntegerField()
    customer_email = models.CharField(max_length=100)
    reseller_id = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(choices=Status_Choices, default=Status.Pending.value)

    access_token = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        null=False,
    )

    def save(self, *args, **kwargs):
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_id} ({self.customer_email})"

# Generated manually
import secrets
from django.db import migrations

def generate_tokens(apps, schema_editor):
    Booking = apps.get_model('core', 'Booking')
    for booking in Booking.objects.filter(access_token__isnull=True):
        booking.access_token = secrets.token_urlsafe(64)
        booking.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_booking_access_token'),  # pas aan naar de laatste migratie van jou
    ]

    operations = [
        migrations.RunPython(generate_tokens),
    ]

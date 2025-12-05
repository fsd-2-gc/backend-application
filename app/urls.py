from django.urls import path
from core.views import health
from core.views import getproducts
from core.views import createproduct
from core.views import getproduct
from core.views import createbooking
from core.views import cancelbooking


urlpatterns = [
    path("v1/health/", health),
    path("v1/getproducts/", getproducts),
    path("v1/createproduct/", createproduct),
    path("v1/getproduct/<int:product_id>/", getproduct),
    path("v1/createbooking/", createbooking),
    path("v1/cancelbooking/<int:booking_id>/", cancelbooking),
]

# JSON error handlers
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
handler400 = 'core.views.error_400'

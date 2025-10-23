from django.urls import path
from core.views import health

urlpatterns = [
    path("v1/health/", health),
]

# JSON error handlers
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'
handler400 = 'core.views.error_400'

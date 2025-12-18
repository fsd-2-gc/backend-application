from django.urls import path
from core.views.getproducts import getproducts  # import the module that has getproducts

urlpatterns = [
    path("api/products/", getproducts),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout, name='checkout'),
    # This will take the order number as an argument,
    # call the 'checkout success' view & be named
    # checkout_success.
    path(
        'checkout_success/<order_number>', views.checkout_success,
        name='checkout_success'),
]

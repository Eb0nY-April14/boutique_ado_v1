from django.urls import path
from . import views
# Since the webhook function will live in a file called webhooks.py,
# we'll import it from .webhooks just as we import other functions.
from .webhooks import webhook

urlpatterns = [
    path('', views.checkout, name='checkout'),
    # This will take the order number as an argument,
    # call the 'checkout success' view & be named
    # checkout_success.
    path(
        'checkout_success/<order_number>', views.checkout_success,
        name='checkout_success'),
    path(
        'cache_checkout_data/', views.cache_checkout_data,
        name='cache_checkout_data'),
    # Since this is related to the checkout app, we'll put it here
    # in its urls.py, call this path WH & it'll return a function
    # called webhook with the name of webhook.
    path('wh/', webhook, name='webhook'),
]

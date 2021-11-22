from django.http import HttpResponse


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    # The init method of the class is a setup method that's
    # called every time an instance of the class is created.
    def __init__(self, request):
        #  We'll use it to assign the request as an attribute of the class
        # just in case we need to access any attributes of the request coming
        # from stripe.
        self.request = request

    # We'll create a class method called handle event which will take the event
    # stripe is sending us & simply return an HTTP response indicating it was
    # received.
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

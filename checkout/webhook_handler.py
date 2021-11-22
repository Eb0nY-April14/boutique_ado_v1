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
    # This generic handle event method will receive the webhook that are
    # otherwise not been handled so we'll change the content to
    # 'unhandled webhook received'.
    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    # For each type of webhook, we want a different method to handle it which
    # makes them easy to manage & makes it easy to add more as stripe adds new
    # ones.
    # The 1st method is called handle_payment_intent_succeeded & its job is to
    # handle the payment intent succeeded webhook from stripe. This will be
    # sent each time a user completes the payment process.
    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    # In the event of their payment failing, we'll have a separate
    # method listening for that webhook.
    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

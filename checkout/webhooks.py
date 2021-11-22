from django.conf import settings
from django.http import HttpResponse
# This 'require_post' decorator makes this view require
# a post request & reject get requests.
from django.views.decorators.http import require_POST
# We'll also import the 'CSRF exempt' since stripe won't
# send a CSRF token like we'd normally need.
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe

@require_POST
@csrf_exempt
# We'll create the webhook function which will take a request.
# The code for this comes directly from stripe with a couple
# of modifications.
def webhook(request):
    """Listen for webhooks from Stripe"""
    # Setup. we'll need to set up the stripe API key & the
    # webhook secret which will be used to verify that the
    # webhook actually came from stripe.
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, wh_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    # We'll add a generic exception handler to catch any
    # exceptions other than the 2 that stripe has provided.
    except Exception as e:
        return HttpResponse(content=e, status=400)

    # Set up a webhook handler. We'll create an instance of
    # the webhook handler & pass in the request.
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions.
    # Below this comment, we'll create a dictionary called 'event map'
    # whose keys will be the names of the webhooks coming from stripe
    # while its values will be the actual methods inside the handler.
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Get the webhook type from Stripe. We'll get the type of
    # the event from stripe & store it in a key called type.
    # This will return something like payment intent.succeeded
    # or payment intent.payment failed.
    event_type = event['type']

    # If there's a handler for it, get it from the event map or
    # use the generic one by default. We'll look up the key in
    # the dictionary & assign its value to a variable called
    # 'event handler'. This 'event handler' is like an alias
    # for whatever function we pulled out of the 'event map'
    # dictionary above so we can call it just like any other
    # function.
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the event handler with the event i.e to get the response
    # from the webhook handler, we can just call 'event handler' &
    # pass it the event.
    response = event_handler(event)
    # Finally, we'll return the response to stripe.
    return response

    # This print & return statements below are used to test that
    # our webhooks is set up & works properly.
    # print('Success!')
    # return HttpResponse(status=200)

from django.http import HttpResponse

from .models import Order, OrderLineItem
from products.models import Product

import json
import time


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
        # This should have our metadata attached. The 'payment intent' will be
        # saved in a key called 'event.data.object'
        intent = event.data.object
        #  Here, we'llget the payment intent id, the shopping bag & the users
        # 'save info' preference from the metadata we added in the last video
        pid = intent.id
        bag = intent.metadata.bag
        save_info = intent.metadata.save_info

        # We'll also store these 3 details below:
        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        grand_total = round(intent.charges.data[0].amount / 100, 2)

        # Clean data in the shipping details. To ensure the data is in the same
        # form as what we want in our database, we'll replace any empty strings
        # in the shipping details with 'None' since stripe will store them as
        # blank strings which is not the same as the null value we want in the
        # database.
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

    # here, we assume that the order doesn't exist by setting the 'order exists'
    # variable to false.
        order_exists = False
        attempt = 1
        # We'll try to get the order using all the information from the payment intent
        # using the iexact lookup field to make it an exact match but case-insensitive.
        # We'll create a while loop that the webhooks handler will execute up to 5 times
        # before giving up to create the order
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    # We'll add the shopping bag & the stripe pid to the list of
                    # attributes we want to match on when finding it in order to
                    # remove all doubt as to whether we're looking for the proper
                    # order in the webhook handler.
                    original_bag=bag,
                    stripe_pid=pid,
                )
                # If the order is found, it should break out of the while loop.
                order_exists = True
                break
            # If the order doesn't exist, we'll create it just like we would if
            # the form were submitted but if the view is slower than the webhooks
            # handler, instead of the webhook handler just immediately going to
            # create the order if it's not found in the database thereby causing
            # duplicate orders when the view finally finishes loading, we'll
            # introduce a bit of delay.
            except Order.DoesNotExist:
                # If the handler does not find the order the first time, instead of
                # creating the order, it'll increment attempt by 1 & then we use python's
                # time module to sleep for 1 second. This will in effect cause the webhook
                # handler to try to find the order 5 times over 5 seconds before giving up
                # & creating the order itself.
                attempt += 1
                time.sleep(1)
        # If 'order exists' has been set to true, we'll return the 200 response.
        if order_exists:
            # If the order is found we'll set order exists to true & return
            # a 200 HTTP response to stripe with the message that we verified
            # the order already exists.
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        # If otherwise i.e 'order exists' is not set to true, we'll create 
        # the order.
        else:
            order = None
            try:
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    country=shipping_details.address.country,
                    postcode=shipping_details.address.postal_code,
                    town_or_city=shipping_details.address.city,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    county=shipping_details.address.state,
                    # If it's not found we'll also want to create the order using 
                    # those items just like we would in the view. This ensures that 
                    # a payment has been processed successfully when we receive a 
                    # webhook from stripe.
                    original_bag=bag,
                    stripe_pid=pid,
                )
                for item_id, item_data in json.loads(bag).items():
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
            except Exception as e:
                # If anything goes wrong, this'll just delete the order if it was created.
                if order:
                    order.delete()
                # It'll then return a 500 server error response to stripe which will cause
                # stripe to automatically try the webhook again later.
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        # This prints out the payment intent (i.e from previous line above) coming
        # from stripe once the user makes a payment. For testing purpose only.
        # print(intent)
        #  At this point in the code we know the order must have been created by the
        # webhook handler so we return a response to stripe indicating that.
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
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

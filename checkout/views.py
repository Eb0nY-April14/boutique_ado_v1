from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
# We'll import the 'bag contents' function from 'bag.contexts' in our
# context.py file in order to make that function available for use here
# in our views.
from bag.contexts import bag_contents

import stripe


# Create your views here.
def checkout(request):
    # 1st, we'll set variables for the public & secret keys below.
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    # First, we'll get the bag from the session.
    bag = request.session.get('bag', {})
    # The 3 lines of code below will be executed if nothing's in the bag
    # i.e add a simple error message & redirect back to the products page.
    # This will prevent people from manually accessing the URL by typing
    # '/checkout'.
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # Since all that the 'bag contents' function returns is a Python
    # dictionary, we can pass it the request & get the same dictionary
    # here in the view & then store that in a variable called 'current bag'
    # so as not to overwrite the bag variable that already exists.
    current_bag = bag_contents(request)

    # To get the total, we'll get the 'grand_total' key out of the current bag,
    # multiply that by a 100 & round it to 0 decimal places using the round
    # function since stripe will require the amount to charge as an integer.
    total = current_bag['grand_total']
    stripe_total = round(total * 100)
    # Next, we'll set the secret key on stripe.
    stripe.api_key = stripe_secret_key
    'Authorization: Bearer stripe.api_key'
    # Here, we'll create the payment intent with stripe.payment
    # intent.create giving it the amount & the currency & just
    # print it out for now.
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # print(intent) Leave it in for debugging purpose

    # We'll create an instance of our order form.
    order_form = OrderForm()

    # We'll add a convenient message here that alerts you if you 
    # forget to set your public key.
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')

    # Then create the template.
    template = 'checkout/checkout.html'
    # Also, we create the context containing the order form.
    context = {
        'order_form': order_form,
        # Copy the public key from Stripe & add it here below to the context.
        # We'll also add a test value below for the 'client secret'.
        # If we open the dev tools by clicking on 'inspect', we'll see that
        # Stripe has converted these 2 values we've given below to ids which
        # matches what we sent here below in the json_script template filter.
        # 'stripe_public_key': 'pk_test_0SMREd7Vdweb1MGRi8S0EycR00JVzSAs5O',
        # 'client_secret': 'test client secret',

        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    #  Finally, we render out everything created above.
    return render(request, template, context)

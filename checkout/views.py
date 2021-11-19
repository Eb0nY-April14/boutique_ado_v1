from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


# Create your views here.
def checkout(request):
    # First, we'll get the bag from the session.
    bag = request.session.get('bag', {})
    # The 3 lines of code below will be executed if nothing's in the bag
    # i.e add a simple error message & redirect back to the products page.
    # This will prevent people from manually accessing the URL by typing
    # '/checkout'.
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # We'll create an instance of our order form.
    order_form = OrderForm()
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
        'stripe_public_key': 'pk_test_0SMREd7Vdweb1MGRi8S0EycR00JVzSAs5O',
        'client_secret': 'test client secret',
    }

    #  Finally, we render out everything created above.
    return render(request, template, context)

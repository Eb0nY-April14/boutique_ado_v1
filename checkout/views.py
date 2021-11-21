from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
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

    # This checks whether the method is 'POST'.
    if request.method == 'POST':
        # In this post method code, we need the shopping bag.
        bag = request.session.get('bag', {})
        # Then we'll put the form data into a dictionary as below.
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # This will create an instance of the form using the form data.
        order_form = OrderForm(form_data)
        # This wll save the order if the form is valid.
        if order_form.is_valid():
            order = order_form.save()
            # We then iterate through the bag items to create each line item.
            for item_id, item_data in bag.items():
                try:
                    # 1st, we get the Product ID out of the bag
                    product = Product.objects.get(id=item_id)
                    # Then if its value is an integer, we know we're working 
                    # with an item that doesn't have sizes so the quantity 
                    # will just be the 'item data'.
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    # But if the item has sizes, we'll iterate through each size 
                    # & create a line item accordingly.
                    else:
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # In case a product isn't found, we'll add an error message,
                # delete the empty order & return/redirect the user to the 
                # shopping bag page. 
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            # Here below & at the same indentation level as the for-loop 
            # above, we'll attach whether or not the user wants to save 
            # their profile information to the session.
            request.session['save_info'] = 'save-info' in request.POST
            # Then, we'll redirect them to a new page called 'checkout success'
            # & pass it the 'order number' as an argument. 
            return redirect(reverse('checkout_success', args=[order.order_number]))
        # The 'else' part on the next line after this comment handles if 
        # the order form isn't valid. It'll display a message to let them know & 
        # then they'll be sent back to the checkout page at the bottom of this view
        # with the form errors shown.
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        # First, we'll get the bag from the session.
        bag = request.session.get('bag', {})
        # The 3 lines of code below will be executed if nothing's in the bag
        # i.e add a simple error message & redirect back to the products page.
        # This will prevent people from manually accessing the URL by typing
        # '/checkout'.
        if not bag:
            messages.error(
                request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        # Since all that the 'bag contents' function returns is a Python
        # dictionary, we can pass it the request & get the same dictionary
        # here in the view & then store that in a variable called 'current bag'
        # so as not to overwrite the bag variable that already exists.
        current_bag = bag_contents(request)

        # To get the total, we'll get the 'grand_total' key out of the current 
        # bag, multiply that by a 100 & round it to 0 decimal places using the 
        # round function since stripe will require the amount to charge as an 
        # integer.
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


# This function will take the order number & render a nice success page
# to let the user know that their payment is complete.
def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # we'll 1st check whether the user wants to save their information 
    # by getting that from the session just like we get the shopping bag
    # & it'll be required once we create user profiles.
    save_info = request.session.get('save_info')
    # Here, we'll use the order number to get the order created in the 
    # previous view which we'll send back to the template.
    order = get_object_or_404(Order, order_number=order_number)
    # Then we'll attach a success message to let the user know what 
    # their order number is & that we'll be sending an email to the 
    # email they put in the form.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # Finally, we'll delete the user shopping bag from the session
    # since it'll no longer be needed for this session.
    if 'bag' in request.session:
        del request.session['bag']

    # These 2 lines of code below set the template & the context.
    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    # This renders the template.
    return render(request, template, context)

from django.shortcuts import (
    render, redirect, reverse, get_object_or_404, HttpResponse
)
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem

from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
# We'll import the 'bag contents' function from 'bag.contexts' in our
# context.py file in order to make that function available for use here
# in our views.
from bag.contexts import bag_contents

import stripe
# We'll import JSON since we're using it to add the bag to the metadata.
import json

# What happens here is that before we call the 'confirm card payment'
# method in the stripe JScript, we'll make a post request to this
# view & give it the client secret from the payment intent
@require_POST
def cache_checkout_data(request):
    try:
        # We'll split that at the word secret & the 1st part of it
        # will be the payment intent Id which will be stored in a
        # variable called pid.
        pid = request.POST.get('client_secret').split('_secret')[0]
        # Next, we'll set up stripe with the secret key so we can
        # modify the payment intent.
        stripe.api_key = settings.STRIPE_SECRET_KEY
        # Then call 'stripe.PaymentIntent.modify', give it the pid
        # & tell it what we want to modify i.e add some metadata.
        # We'll then add the user who's placing the order, whether
        # or not they wanted to save their information & most
        # importantly, add a JSON dump of their shopping bag which
        # we'll use a little later.
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        # We'll return an HTTP response with the 200 status for okay.
        return HttpResponse(status=200)
    # The 'except' block handles if anything goes wrong. We'll just
    # add a message & return a response with the error message content
    # & a status of 400 for bad request.
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)

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
        # This wll save the order if the form is valid. We'll also get
        # the client secret added as an hidden input to the form in the
        # check out page if the order form is valid.
        if order_form.is_valid():
            # To prevent multiple save events from being executed on
            # the database, we'll add 'commit equals false' here below
            # to prevent the 1st one from happening.
            order = order_form.save(commit=False)
            # We'll then split it to get the payment intent id as we did
            # in the 'cache check out data' view.
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            # We'll also add the shopping bag here by simply using dumps
            # to dump it to a JSON string & set it on the order.
            order.original_bag = json.dumps(bag)
            # Then save the order.
            order.save()

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

        # Attempt to prefill the form with any info the user maintains in 
        # their profile i.e since users now have profiles, we can use their 
        # default delivery information to pre-fill the form on the checkout 
        # page. It checks if the user is authenticated & if so, get their 
        # profile & use the initial parameter on the order form to pre-fill 
        # all its fields with the relevant information e.g we can fill in the 
        # full_name with the built in get_full_name method on their user 
        # account, their email from their user account & everything else from 
        # the default information in their profile.
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                    'country': profile.default_country,
                    'postcode': profile.default_postcode,
                    'town_or_city': profile.default_town_or_city,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'county': profile.default_county,
                })
            # If the user is not authenticated, we'll render an empty form 
            except UserProfile.DoesNotExist:
                order_form = OrderForm()

        # print(intent) Leave it in for debugging purpose

        # We'll create an instance of our order form.
        else:
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

    # Since we already know the form has been submitted & the order success-
    # fully processed, we'll now add the user profile to it. To add the pro-
    # file, we have to check if the user is authenticated because if so they
    # 'll have a profile that was created when they created their account.
    if request.user.is_authenticated:
        # Here, We'll get the user's profile if authenticted
        profile = UserProfile.objects.get(user=request.user)
        # Set it on the order i.e attach the user's profile to the order
        order.user_profile = profile
        # Then save it.
        order.save()

        # We'll use the 'save info' box here to save the user's info, 
        # determine if it was checked 1st & if so, we can pull the data 
        # to go in the user's profile of the order into a dictionary of 
        # profile data. 
        if save_info:
            # The dictionary's keys below should match the fields 
            # on the user profile model i.e default phone number, 
            # country, postcode etc.
            profile_data = {
                'default_phone_number': order.phone_number,
                'default_country': order.country,
                'default_postcode': order.postcode,
                'default_town_or_city': order.town_or_city,
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_county': order.county,
            }
            # We'll create an instance of the user profile form, using 
            # the profile data & tell it we're going to update the profile 
            # we've obtained above.
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            # This saves the form if form is valid 
            if user_profile_form.is_valid():
                user_profile_form.save()

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

from django.shortcuts import render, redirect, reverse, HttpResponse, get_object_or_404
from django.contrib import messages

from products.models import Product

# Create your views here.


def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

# The form we created in product_detail.html is submitted to this view
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # This below will get the product or return 404 error if not found
    product = get_object_or_404(Product, pk=item_id)
    # On the next line, we'll get the quantity from the form.
    quantity = int(request.POST.get('quantity'))
    # The code below this comment will get the redirect URL from the form
    # so as to know where to redirect once the process here is finished.
    redirect_url = request.POST.get('redirect_url')
    size = None
    # This will update all products that should have sizes in all our views
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    # In modern versions of HTTP, every request-response cycle between
    # the server & the client which in our case is between the django
    # view on the server-side & our form making the request on the
    # client-side uses a 'session' to allow information to be stored
    # until the client & server are done communicating. This is very
    # handy mostly in an e-commerce store as it allows us to store the
    # contents of the shopping bag in the HTTP session while the user
    # browses the site & adds items to be purchased. By storing the
    # shopping bag in the session, they can add something to the bag,
    # then browse to a different part of the site, add something else &
    # so on without losing the contents of their bag. The session will
    # persist until the user closes their browser. To implement this
    # concept, we'll create a variable named bag which accesses the
    # requests session & tries to get this variable if it already exists
    # & if it doesn't, initializes it to an empty dictionary. It checks
    # if there's a bag variable in the session & creates one if not.
    # We'll get the bag session variable if it exists or create it if
    # it doesn't.
    bag = request.session.get('bag', {})

    if size:
        # This checks if the item is already in the bag & if it is, then we
        # need to check if another item of the same id & same size already
        # exists & if so, increment the quantity for that size or else set
        # it equal to the quantity.
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
                messages.success(
                    request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
            messages.success(
                request, f'Added size {size.upper()} {product.name} to your bag')
    # This else part below takes care of products with no size
    else:
        # This will stuff the product into the dictionary we just created
        # along with the quantity & will do so by creating a key of the
        # items id & set it equal to the quantity. If the item is already
        # in the bag i.e there's already a key in the bag dictionary
        # matching this product id, then we'll increment its quantity rightly
        if item_id in list(bag.keys()):
            # This updates the item quantity if it already exists
            bag[item_id] += quantity
            messages.success(
                request, f'Updated {product.name} quantity to {bag[item_id]}')
            # The else part below adds the item to the bag for the 1st time as
            # a dictionary with a key of items_by_size.
        else:
            bag[item_id] = quantity
            # We'll then use the messages dot success function to add a message
            # to the request object & use some string formatting to let the
            # user know they've added this product to their bag.
            # messages.success(request, f'Added {product.name} to your bag')
            messages.success(request, f'Added {product.name} to your bag')

    # Here, we'll overwrite the session variable called bag with the updated
    # version.
    request.session['bag'] = bag
    # print(request.session['bag'])
    return redirect(redirect_url)


# This view is similar to the 'add to bag' view above it & its purpose is to
# update the quantity of an item in the shopping bag already.
def adjust_bag(request, item_id):
    """Adjust the quantity of the specified product to the specified amount"""

    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity'))
    size = None
    if 'product_size' in request.POST:
        size = request.POST['product_size']
    bag = request.session.get('bag', {})

    # This comes from a form on the 'shopping bag' page which will
    # contain the new quantity the user wants in the bag. If the item
    # has a size, we'll need to drill into the 'items by size' dictionary,
    # find that specific size & either set its quantity to the updated one
    # or (i.e else part below) remove it if the quantity submitted is zero.
    if size:
        # If quantity is greater than 0, we'll set the items quantity
        # rightly or else (else part below) remove the item.
        if quantity > 0:
            bag[item_id]['items_by_size'][size] = quantity
            messages.success(
                request, f'Updated size {size.upper()} {product.name} quantity to {bag[item_id]["items_by_size"][size]}')
        else:
            del bag[item_id]['items_by_size'][size]
            # If that's the only size they had in the bag i.e if the 'items by
            # size' dictionary is now empty which will evaluate to false, we'll
            # remove the entire 'item id' so that there's no empty 'items by
            # size' dictionary hanging around.
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(
                request, f'Removed size {size.upper()} {product.name} from your bag')
    # The else part here below takes care of items with no size
    else:
        if quantity > 0:
            bag[item_id] = quantity
            messages.success(
                request, f'Updated {product.name} quantity to {bag[item_id]}')
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

    request.session['bag'] = bag
    # Lastly, we'll redirect back to the view bag URL using the reverse
    # function for that.
    return redirect(reverse('view_bag'))


# The 'remove from bag' view below will allow users to remove items directly
# without setting the quantity to 0 manually & is similar to both views above.
def remove_from_bag(request, item_id):
    """Remove the item from the shopping bag"""

    # We wrapped this entire block of code in a try block to catch any
    # exceptions that may happen & then return a 500 server error.
    try:
        product = get_object_or_404(Product, pk=item_id)
        size = None
        if 'product_size' in request.POST:
            size = request.POST['product_size']
        bag = request.session.get('bag', {})

        # If the user is removing a product with sizes, we want to remove only
        # the specific size they requested so if size is in request.post, we'll
        # delete that size key in the items by size dictionary.
        if size:
            del bag[item_id]['items_by_size'][size]
            # If that's the only size they had in the bag i.e if the 'items by
            # size' dictionary is now empty which will evaluate to false, we'll
            # remove the entire 'item id' so that there's no empty 'items by
            # size' dictionary hanging around.
            if not bag[item_id]['items_by_size']:
                bag.pop(item_id)
            messages.success(
                request, f'Removed size {size.upper()} {product.name} from your bag')
        # The else part here below takes care of items with no size
        else:
            bag.pop(item_id)
            messages.success(request, f'Removed {product.name} from your bag')

        request.session['bag'] = bag
        # Since this view will be posted to from a JScript function, instead
        # of returning a redirect, we want to return an actual 200 HTTP
        # response to show that the item was successfully removed.
        return HttpResponse(status=200)

    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return HttpResponse(status=500)

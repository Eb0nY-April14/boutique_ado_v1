from django.shortcuts import render, redirect

# Create your views here.


def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

# The form we created in product_detail.html is submitted to this view
def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    # On the next line below, we get the quantity from the form.
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
        # This checks if the item is already in the bag & if it is, then we need 
        # to check if another item of the same id & same size already exists & if 
        # so, increment the quantity for that size or else set it equal to the quantity.
        if item_id in list(bag.keys()):
            if size in bag[item_id]['items_by_size'].keys():
                bag[item_id]['items_by_size'][size] += quantity
            else:
                bag[item_id]['items_by_size'][size] = quantity
        else:
            bag[item_id] = {'items_by_size': {size: quantity}}
    # This else part below takes care of products with no size
    else:
        # This will stuff the product into the dictionary we just created along
        # with the quantity & will do so by creating a key of the items id & set
        # it equal to the quantity. If the item is already in the bag i.e there's
        # already a key in the bag dictionary matching this product id, then we'll
        # increment its quantity rightly
        if item_id in list(bag.keys()):
            # This updates the item quantity if it already exists
            bag[item_id] += quantity
            # The else part below adds the item to the bag for the 1st time as a 
            # dictionary with a key of items_by_size.
        else:
            bag[item_id] = quantity 

    # Here, we'll overwrite the session variable called bag with the updated version.
    request.session['bag'] = bag
    # print(request.session['bag'])
    return redirect(redirect_url)

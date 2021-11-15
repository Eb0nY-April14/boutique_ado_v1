from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product



# We'll create a function called bag_contents which will take
# request as a parameter & return a dictionary called context.
def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    # To access the shopping bag in the session, we'll use an 
    # if statement to get the bag if it already exists or 
    # initialize it to an empty dictionary if not.
    bag = request.session.get('bag', {})

    # To populate the values of the 'bag_items' variables we 
    # created earlier but has not used yet, we need to iterate 
    # through all the items in the shopping bag, tally up the 
    # total cost and product count & add the products & their 
    # data to the bag_items list. 
    # NOTE that the variable bag used in the code after this 
    # comment is from the request.session in the previous 
    # code above. 
    for item_id, quantity in bag.items():
        # We'll 1st get the product
        product = get_object_or_404(Product, pk=item_id)
        # Then add its quantity & multiply by the price to get the total.
        total += quantity * product.price
        # Then we increment the product count by the quantity.
        product_count += quantity
        # We'll add a dictionary to the list of bag_items containing not
        # only the id & the quantity but also the product object itself 
        # as that will give us access to all the other fields such as the 
        # product image etc when we iterate through the bag items in our 
        # templates.
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        # The line of code after this comment lets the user know how
        # much more they need to spend to get free delivery
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    # The grand total is calculated by adding the delivery charge to the total
    grand_total = delivery + total

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context

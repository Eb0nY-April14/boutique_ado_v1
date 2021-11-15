from decimal import Decimal
from django.conf import settings

# We'll create a function called bag_contents which will take
# request as a parameter & return a dictionary called context.
def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0

    # Since we want to give customers free delivery if they
    # spend more than the amount specified in the free delivery
    # threshold in settings.py, we'll use if statement to check
    # for this.
    # If total is less than the threshold, we'll calculate
    # delivery cost as the total multiplied by the standard
    # delivery percentage from settings.py which in this case
    # is 10% but if If greater than or equal to the threshold,
    # the else part kicks in where we'll set delivery & the
    # free_delivery_delta to zero.
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

    # This is known as a context processor & its purpose is to make
    # this dictionary available to all templates across the entire
    # application. To make this context processor available to the
    # entire application, we need to add it to the list of context
    # processors in the templates variable in settings.py.
    # This context used here is same as the ones we've been using
    # in our views but the only difference is we're returning it
    # directly and making it available to all templates by putting
    # it in settings.py.

    # The final step here is to add all these items i.e bag items,
    # total, product count, delivery, free_delivery_delta,
    # free_delivery_threshold & grand_total to the context so they'll
    # be available in templates across the site. This means that
    # everything in this context will be available in every template &
    # app across the entire project
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

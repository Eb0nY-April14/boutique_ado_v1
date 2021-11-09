from django.shortcuts import render
from .models import Product

# Create your views here.


def all_products(request):
    """ A view to show all products including sorting and search queries """

    # This will return all products from the database
    # using product.objects.all
    products = Product.objects.all()

    # We'll add 'products' to the context so that it'll
    # be available in the template.
    context = {
        'products': products,
    }

    # It'll also need a context since we need to send some
    # things back to the template.
    return render(request, 'products/products.html', context)

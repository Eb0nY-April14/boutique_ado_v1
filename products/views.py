from django.shortcuts import render, get_object_or_404
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


def product_detail(request, product_id):
    """ A view to show individual product details """

    # This will return only one product so we'll use 'get object or 404' that
    # takes in the Product & the product ID as parameters.
    product = get_object_or_404(Product, pk=product_id)

    # We'll add 'product' to the context to reflect the detail of only 1
    # product so that it'll be available in the template.
    context = {
        'product': product,
    }

    # It'll also need a context since we need to send some
    # things back to the template.
    return render(request, 'products/product_detail.html', context)

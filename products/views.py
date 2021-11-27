from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category
from .forms import ProductForm


# Create your views here.


def all_products(request):
    """ A view to show all products, including sorting and search queries """

    products = Product.objects.all()
    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'
            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                # This message below shows up if the user submits a search
                # with no search criteria.
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            queries = Q(
                name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)

# What this view does is that it'll render an empty instance of our 
# form so we can see how it looks
def add_product(request):
    """ Add a product to the store """
    # If the request method is post, we'll instantiate a new instance 
    # of the product form from request.post & include request.files also
    # in order to make sure that the image of the product is captured if 
    # submitted.
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        # If form.is_valid, we'll save it, add a success message
        # & redirect to the same view.
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('add_product'))
        # But if there are any errors on the form, we'll attach a generic 
        # error message to tell the user to check their form which will 
        # display the errors.
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    # This empty form instantiation here below is put into an else block
    # so it doesn't wipe out the form errors.
    else:
        form = ProductForm()
    # This will use a new template called 'add_product'
    template = 'products/add_product.html'
    # It'll also include a context that has the product form.
    context = {
        'form': form,
    }

    return render(request, template, context)

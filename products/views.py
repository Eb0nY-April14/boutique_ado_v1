from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q  # used to generate a search query.
from .models import Product, Category

# Create your views here.

def all_products(request):
    """ A view to show all products including sorting and search queries """

    # This will return all products from the database
    # using product.objects.all
    products = Product.objects.all()
    # We'll start with making the 'query' equals to none at the top of this
    # view to ensure we don't get an error when loading the products page
    # without a search term.
    query = None
    # We'll start by making 'category' equals to none at the top of the view.
    categories = None
    sort = None
    direction = None

    # We can access those url parameters in the 'all_products' view
    # by checking whether 'request.get' exists.
    if request.GET:
        if 'sort' in request.GET:
            # The reason for copying the sort parameter into a new variable
            # called sortkey is because we want to preserve the original
            # field we want it to sort on name. Now we have the actual field
            # we're going to sort on, lower_name in the sort key variable.
            # If we had just renamed sort itself to lower_name, we would have
            # lost the original field name.
            # Here, we'll get the 'sort' which is equal to None at this point
            # & set it to sortkey variable as done on next line
            sortkey = request.GET['sort']
            # We'll set the 'sort' up above that was equal to None
            # earlier to that sort key.
            sort = sortkey
            # To allow case-insensitive sorting on the name field,
            # we need to 1st annotate all the products with a new field.
            # Annotation allows us to add a temporary field on a model so
            # in this case, what we want to do is check whether the sort
            # key is equal to name.
            if sortkey == 'name':
                # if the condition above is true, we'll set it to lower_name
                # i.e rename sortkey to lower_name which is the field we're
                # about to create with the annotation.
                sortkey = 'lower_name'
                # The code on the next line will do the annotation. We'll
                # annotate the current list of products with a new field.
                products = products.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                # All we'll do here is check whether the direction is
                # descending. If so, we'll add a minus in front of the
                # sort key using string formatting, which will reverse
                # the order.
                if direction == 'desc':
                    sortkey = f'-{sortkey}'

            # Finally, all we need to do to actually sort the products is 
            # use the 'order by' model method.
            products = products.order_by(sortkey)

        # Then we'll check whether category exists in request.get & split it
        # into a list at the commas if it does exist.
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            # We'll then use that list created above to filter the current
            # query set of all products down to only products whose category
            # name is in the list rom the URL.
            products = products.filter(category__name__in=categories)

            # And then we'll filter all categories down to the ones whose name
            # is in the list from the URL. Doing this will convert the list of
            # strings of category names passed through the URL into a list of
            # actual category objects so that we can access all their fields
            # in the template.
            categories = Category.objects.filter(name__in=categories)

        # We'll check if 'q' is in request.get where 'q' is the name
        # we gave the text input in the form on 'mobile top header.html'
        # & base.html pages
        if 'q' in request.GET:
            query = request.GET['q']
            # If the search query is blank, no results will be returned.
            # We can then use the Django messages framework to attach an
            # error message to the request & then redirect back to the
            # products url.
            if not query:
                messages.error(
                    request, "You didn't enter any search criteria!")
                return redirect(reverse('products'))

            # In django, if we use product.objects.filter in order to
            # filter a list of products, in the case of our queries that
            # means that in order for the query submitted by a user to
            # match, the term has to appear in both the product's name &
            # description but since we want to return results where the
            # query was matched in either the product name OR the description,
            # we need to use Q. This is worth knowing because in real-world
            # database operations, queries can become quite complex & using Q
            # is often the only way to handle them.

            # To use Q, we'll set a variable equal to a Q object where the name
            # contains the query OR the description contains the query. The pipe
            # is what generates the OR statement & the 'i' in front of contains
            # makes the queries case insensitive.
            queries = Q(name__icontains=query) | Q(description__icontains=query)
            # We'll then pass the 'queries' to the filter method in order to
            # actually filter the products as done on the next line
            products = products.filter(queries)

        # Lastly, we need to return the current sorting methodology to 
        # the template. There are plenty of ways to do this but since
        # we have both the sort & direction variables stored, it's easy 
        # to do that with string formatting. We'll call this variable 
        # 'current_sorting' & then return it to the template. NOTE that
        # the value of this variable will be the string none_none if 
        # there's no sorting.
        current_sorting = f'{sort}_{direction}'

        # We'll add 'products' to the context so that it'll
        # be available in the template.
        context = {
            'products': products,
            'search_term': query,  # add the query to the context
            # We'll return that list of 'category objects' called
            # 'current_categories' to the context so we can use it
            # in the template later on
            'current_categories': categories,
            'current_sorting': current_sorting,
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

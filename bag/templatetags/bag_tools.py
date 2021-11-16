# THIS IS WHERE THE SUBTOTAL IN THE SHOPPING BAG PAGE IS BEING CALCULATED. THE
# FUNCTION NAME IS calcunderscoresubtotal

# Creating 2 new files named 'bag tools.py' & 'underscorex2initunderscorex2.py' 
# inside the folder called 'template tags' will ensure that this directory 
# is treated as a Python package making our 'bag tools' module available for 
# imports & to use in templates.

from django import template


# NOTE: All these code are directly from the django documentation & for more
# clarity, go there & look up 'creating custom template tags & filters'.
# To register this filter, we need to create a variable called 'register' 
# which is an instance of template.library.
register = template.Library()

# We'll then use the register filter decorator to register our function as a template filter.
@register.filter(name='calc_subtotal')
# This function calculates the subtotal in the 'shopping bag' page. It takes in price & 
# quantity as parameters & returns their product.
def calc_subtotal(price, quantity):
    return price * quantity
from django import forms
from .models import Product, Category


# We'll create a new class called 'ProductForm' which will extend the built
# in 'forms.modelform' & have an inner metaclass that defines the model &
# the fields we want to include.
class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        # We'll use a special dunder or double underscore string called 'all'
        # which will include all the fields.
        fields = '__all__'

    # We'll override the init method to make a couple changes to the fields.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # This gets all the categories.
        categories = Category.objects.all()
        # We'll create a list of tuples of the friendly names associated with
        # their category ids. This special syntax is called the list comprehe-
        # nsion & is just a shorthand way of creating a for loop that adds
        # items to a list.
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        # We'll update the category field on the form to use the ones for
        # choices instead of using the id. The effect of this will be seen
        # in the select box that gets generated in the form so instead of
        # seeing the category ID or the name field we'll see the friendly name.
        self.fields['category'].choices = friendly_names
        # Lastly, we'll iterate through the rest of these fields & set some
        # classes on them so thay match the theme of the rest of our store.
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'

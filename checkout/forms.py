from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    # We'll give this form some meta options to tell django which
    # model it'll be associated with & which fields we want to render.
    # NOTE: We didn't render any fields in the form which will be
    # automatically calculated because no one will ever be filling that
    # information out, it'll all be done via the model methods we've created.
    class Meta:
        model = Order
        fields = ('full_name', 'email', 'phone_number',
                  'street_address1', 'street_address2',
                  'town_or_city', 'postcode', 'country',
                  'county',)

    # Here, we'll override the init method of the form which will allow us to
    # customize it a bit.
    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels and set autofocus on first field
        """
        # 1stly On the next line after this comment, we'll call the default init
        # method to set the form up as it would be by default.
        super().__init__(*args, **kwargs)
        # Next, we create a dictionary of placeholders that will show up in the
        # form fields instead of clunky looking labels & empty text boxes in the template.
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            # 'country': 'Country',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
        }

    # Here we'll set the autofocus attribute on the full name field to true
    # so the cursor will start in the full name field when the user loads the page.
        self.fields['full_name'].widget.attrs['autofocus'] = True
        # Lastly, we iterate through the forms fields
        for field in self.fields:
            if field != 'country':
                # This will add a star to the placeholder if it's a required
                # field on the model.
                if self.fields[field].required:
                    placeholder = f'{placeholders[field]} *'
                else:
                    placeholder = placeholders[field]
                # This sets all the placeholder attributes to their values in the
                # dictionary above.
                self.fields[field].widget.attrs['placeholder'] = placeholder
            # We add a CSS class that we'll use in base.css file later
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            # This will remove the form fields labels since we won't need
            # them given the placeholders are now set.
            self.fields[field].label = False

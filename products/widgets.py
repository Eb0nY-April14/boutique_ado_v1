from django.forms.widgets import ClearableFileInput
from django.utils.translation import gettext_lazy as _


# This newly created class with the same name
# inherits from the built-in one.
class CustomClearableFileInput(ClearableFileInput):
    # We'll override the clear checkbox label, the initial text, the
    # input text & the template name with our own values.
    clear_checkbox_label = _('Remove')
    initial_text = _('Current Image')
    input_text = _('')
    template_name = 'products/custom_widget_templates/custom_clearable_file_input.html'

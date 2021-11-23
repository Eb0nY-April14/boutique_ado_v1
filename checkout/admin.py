from django.contrib import admin
from .models import Order, OrderLineItem


# Register your models here.
# Here, this 'line item' will allow us to add & edit 'line items' in the admin
# right from inside the order model so when we look at an order, we'll see a 
# list of editable line items on the same page rather than having to go to the 
# 'order line item' interface.
class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    # Here on the next line, we'll make the 'line item total' in the form read-only.
    readonly_fields = ('lineitem_total',)


# Within this class, we'll add some read-only fields. These are fields 
# that will be calculated by our model methods such as order number, 
# date, delivery cost, order total & grand_total so we don't want anyone 
# to have the ability to edit them else it could compromise the integrity 
# of an order.
class OrderAdmin(admin.ModelAdmin):
    # Then we'll add the above class to the 'Order Admin' interface i.e 
    # adding the inlines option here in the 'Order Admin' class.
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost', 'order_total',
                       'grand_total', 'original_bag',
                       'stripe_pid')

    # We'll use the fields option here to allow us specify the order 
    # of the fields in the admin interface which would otherwise be 
    # adjusted by django due to the use of some read-only fields.
    # Specifying these fields will make the order stays the same as 
    # it appears in the model.
    fields = ('order_number', 'date', 'full_name',
              'email', 'phone_number', 'country',
              'postcode', 'town_or_city', 'street_address1',
              'street_address2', 'county', 'delivery_cost',
              'order_total', 'grand_total', 'original_bag',
                       'stripe_pid')

    # We'll use this 'list display' option below to restrict the columns 
    # that show up in the order list to only a few key items & set them 
    # to be ordered by date in reverse chronological order putting the 
    # most recent orders at the top.
    list_display = ('order_number', 'date', 'full_name',
                    'order_total', 'delivery_cost',
                    'grand_total',)

    ordering = ('-date',)

# Finally, we'll register the 'Order' model & 'OrderAdmin' but we'll skip 
# registering the 'OrderLineItem' model since it's accessible via the 
# inline on the order model.
admin.site.register(Order, OrderAdmin)

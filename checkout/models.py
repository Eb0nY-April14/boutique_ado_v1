import uuid  # For generating the order number.

from django.db import models
from django.db.models import Sum
from django.conf import settings

# We'll import from product model since the 'order line item'
# model has a foreign key to it.
from products.models import Product


# Create your models here. These models will be used to create
# & track orders for anyone who makes a purchase.
class Order(models.Model):
    # The editable equals false attribute on the order number field
    # will be used to automatically generate this order number & we
    # want it to be unique & permanent so users can find their previous
    # orders. The 'Order' model will handle all orders across the store
    # & will be related to another model called 'order line item'.
    order_number = models.CharField(max_length=32, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    county = models.CharField(max_length=80, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)  # date order was created
    # The last 3 fields below will be calculated using a model method
    # whenever an order is saved.
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2, null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0)

    # This method is called 'generate order number' & it's prepended with an
    # underscore by convention to indicate it's a private method which will
    # only be used inside this class & it will return uuid.uuid4().hex.upper()
    # which will just generate a random string of 32 characters we can use as
    # an order number.
    def _generate_order_number(self):
        """
        Generate a random, unique order number using UUID
        """
        return uuid.uuid4().hex.upper()

    # This method will update the grand total using the aggregate function
    # which works by using the sum function across all the 'line-item' total
    # fields for all line items on this order.
    def update_total(self):
        """
        Update grand total each time a line item is added,
        accounting for delivery costs.
        """
        # The default behaviour is to add a new field to the query set called
        # 'line-item total sum', we can then 'get' & 'set' the order total to
        # that as done on the next line below.
        # Adding 'or 0' to the end of this line that aggregates all the 'line
        # item totals' will prevent an error if we manually delete all the
        # line items from an order. It'll set the order total to 0 instead
        # of None.
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum'] or 0
        # We'll then calculate the delivery cost using the 'free delivery
        # threshold' & the 'standard delivery percentage' from our settings
        # file if the order total is lower than the threshold.
        if self.order_total < settings.FREE_DELIVERY_THRESHOLD:
            # If 'or 0' isn't added to the code on previous line above, this
            # next line would cause an error as it would try to determine if
            # None is less than or equal to the delivery threshold.
            self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        # The else part below sets the delivery cost to 0 if the order total
        # is higher than the threshold..
        else:
            self.delivery_cost = 0
        # Finally, we'll calculate the grand total by adding the order total
        # & the delivery cost together.
        self.grand_total = self.order_total + self.delivery_cost
        # We then save the instance
        self.save()

    # This will override the default save method so that if the order we're saving
    # right now doesn't have an order number, we'll call the 'generate order number'
    # method & then execute the original save method.
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number
        if it hasn't been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    # Here, we'll add the standard string method that returns
    # just the order number for the order model.
    def __str__(self):
        return self.order_number


# An 'Order Line Item' will be like an individual shopping bag item relating to
# a specific order & referencing the product itself, size selected, quantity
# & the total cost for that line item. The basic idea here is when a user checks
# out, the information they put into the payment form will 1st be used to create
# an order instance & then we'll iterate through the items in the shopping bag,
# create an 'order line item' for each one, Attach it to the order & update the
# delivery cost, order total & grand total along the way.
class OrderLineItem(models.Model):
    # On this order line item model, there's a foreign key to the order with a
    # related name of 'line items' so when accessing orders, we'll be able to
    # make calls such as 'order.lineitems.all' & 'order.lineitems.filter' etc
    order = models.ForeignKey(Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems')
    # There's also a foreign key to the product for this line item so that we
    # can access all the fields of the associated product as well.
    product = models.ForeignKey(Product, null=False, blank=False, on_delete=models.CASCADE)
    product_size = models.CharField(max_length=2, null=True, blank=True) # XS, S, M, L, XL
    quantity = models.IntegerField(null=False, blank=False, default=0)
    # NOTE: The line item total is not editable.
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=False, blank=False, editable=False)

    # We also need to set the 'line-item total' field on the 'order line-item'
    # model by overriding its save method. All we need to do is multiply the
    # product price by the quantity for each line item.
    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total
        and update the order total.
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    # Here, we'll add the standard string method as above that returns the SKU
    # of the product & the order number it's part of for each order line item.
    def __str__(self):
        return f'SKU {self.product.sku} on order {self.order.order_number}'

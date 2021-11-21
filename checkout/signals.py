# What this import on the 4th line implies is that these
# signals are sent by django to the entire application
# after a model instance is 'saved' & after it's 'deleted'
# respectively.
from django.db.models.signals import post_save, post_delete
# The import on the next line will receive the 'save' &
# 'delete' signals
from django.dispatch import receiver

# We need this to listen for signals from the
# 'OrderLineItem' model
from .models import OrderLineItem

# We need a way to update the order total, delivery cost &
# grand_total for each order as users add line items to it.
# The basic process for this is to 1st create an order, then
# iterate through the shopping bag & add line items to it one
# by one, updating the various costs along the way. We have
# the method to update the total already in the 'Order' model
# so we just need a way to call it each time a line item is
# attached to the order. To do this, we'll use a built-in
# feature of django called signals.

# To execute this function anytime the post_save signal is sent,
# we'll use the receiver decorator to tell it we're receiving
# post saved signals from the 'OrderLineItem' model.
@receiver(post_save, sender=OrderLineItem)
# This is a special type of function which will handle signals
# from the post_save event. These parameters being taken in as
# arguments refer to the 'sender' of the signal which in our
# case 'OrderLineItem', the actual 'instance' of the model that
# sent it, a boolean sent by django referring to whether this is
# a newly 'created'/'updated' instance & any 'keyword arguments'.
# NOTE: WE NEED TO LET DJANGO KNOW THAT THERE'S A NEW SIGNALS
# MODULE WITH SOME LISTENERS IN IT BY MAKING A SMALL CHANGE TO
# apps.py TO OVERRIDE THE 'ready' METHOD & IMPORT OUR SIGNALS
# MODULE.
def update_on_save(sender, instance, created, **kwargs):
    """
    Update order total on lineitem update/create
    """
    # We'll access 'instance.order' which refers to the order
    # this specific 'line item' is related to & call the
    # update_total method on it.
    instance.order.update_total()

# This will handle updating the various totals when a line item is deleted.
@receiver(post_delete, sender=OrderLineItem)
def update_on_delete(sender, instance, **kwargs):
    """
    Update order total on lineitem delete
    """
    # This print statement below is used to check
    # that the signals & all our setup are working
    # print('delete signal received!')
    instance.order.update_total()

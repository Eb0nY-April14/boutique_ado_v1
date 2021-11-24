from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django_countries.fields import CountryField


# Create your models here.
# We'll create a user profile model which has a one-to-one field attached
# to the user. This is similar to a foreign key except that it specifies
# that each user can only have one profile & each profile can only be
# attached to one user.
class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # The rest of the fields in this model are the delivery information
    # fields we want the user to be able to provide defaults for. These
    # can come directly from the order model.
    # NOTE: All these fields are optional here in the profile
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True)
    default_street_address1 = models.CharField(
        max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(
        max_length=40, null=True, blank=True)
    default_county = models.CharField(
        max_length=80, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(
        blank_label='Country', null=True, blank=True)

    # This string method returns the user name.
    def __str__(self):
        return self.user.username

# This adds a quick receiver for the 'post save' event from the user model
# so that each time a user object is saved, we'll automatically either create
# a profile for them if the user has just been created or just save the profile
# to update it if the user already existed.
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    # If the user has just been created, it automatically
    # create a profile for them
    if created:
        UserProfile.objects.create(user=instance)
    # Existing users: just save the profile to update it
    instance.userprofile.save()

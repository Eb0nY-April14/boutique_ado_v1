from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    # We create a string method that takes in the category model itself & returns the
    # category name
    def __str__(self):
        return self.name

    # This takes in self i.e the 'friendly name' & returns the friendly name
    def get_friendly_name(self):
        return self.friendly_name


# The fields that are required in this Product model are name, description & price
# while the rest are optional.
class Product(models.Model):
    # The 1st field is a foreign key to the category model. We'll allow this to be null 
    # in the database & blank in forms. If a category is deleted, we'll set any products 
    # that use it to have null for this field rather than deleting the product.
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL )
    sku = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    has_sizes = models.BooleanField(null=True, blank=True, default=False)

    #  The string method below will just return the products name 
    def __str__(self):
        return self.name


from django.contrib import admin
from .models import Product, Category

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    # The 'list display' attribute below is a tuple that tells
    # the admin which fields to display. if we want to change the
    # order of the columns in the admin, it can be adjusted here in
    # the 'list display' attribute.
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )

    # We'll sort the products by 'SKU' using the ordering attribute
    # since it's possible to sort on multiple columns. NOTE: This has
    # to be a tuple even though it's only one field. To reverse it, just
    # stick a minus in front of SKU.
    ordering = ('sku',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )

# Here, we'll register our 2 new classes alongside their respective models.
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

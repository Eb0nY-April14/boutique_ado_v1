from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


# We'll create a custom class called 'staticstorage' which will
# inherit from django storages giving it all its functionality.
# We'll then tell it we want to store static files in a location
# from the settings that we'll define in just a moment.
class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION


# This one is similar to the class above
class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION

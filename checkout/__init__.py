# This code here tells django the name of the default config 
# class for the app which is checkout.apps.CheckoutConfig &
# without this line in the init file, django wouldn't know 
# about our custom ready method so our signals wouldn't work.
# This class is in our apps.py
default_app_config = 'checkout.apps.CheckoutConfig'
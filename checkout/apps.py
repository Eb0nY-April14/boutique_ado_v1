from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = 'checkout'

    # To let django know that there's a new signals module in signals.py with some 
    # listeners in it, we've just made a small change to this file we're in called 
    # apps.py overriding the ready method & importing our signals module.
    # With that done, every time a line item is saved or deleted, our custom 'update 
    # total' model method will be called to update the 'order totals' automatically.
    def ready(self):
        import checkout.signals

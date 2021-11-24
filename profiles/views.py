from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from .models import UserProfile
from .forms import UserProfileForm


# Create your views here.
# This view returns a profile.html template with an empty context for now.
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    # This is the post handler for the profile view.
    if request.method == 'POST':
        # All it does is if the request method is post, it creates a new
        # instance of the user profile form using the post data & tell
        # it the instance we're updating is the profile we've just
        # retrieved above.
        form = UserProfileForm(request.POST, instance=profile)
        # It checks if the form is valid & if so, save it & add a success
        # message.
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    # What the rest of the logic below does is replace the form variable
    # with the user's updated profile & then return the same template.

    # This populate the form with the user's current profile information.
    form = UserProfileForm(instance=profile)
    # We'll use the profile & the related name on the order model to get
    # the users orders & return those to the template instead.
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    # Then return the populated 'form' & 'orders' created above to the template
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)

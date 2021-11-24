from django.shortcuts import render, get_object_or_404

from .models import UserProfile


# Create your views here.
# This view returns a profile.html template with an empty context for now.
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    template = 'profiles/profile.html'
    context = {
        'profile': profile,
    }

    return render(request, template, context)

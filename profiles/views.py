from django.shortcuts import render


# Create your views here.
# This view returns a profile.html template with an empty context for now.
def profile(request):
    """ Display the user's profile. """

    template = 'profiles/profile.html'
    context = {}

    return render(request, template, context)

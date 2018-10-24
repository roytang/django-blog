from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

import facebook.djangofb as facebook

from fbtest.models import FacebookUser

@facebook.require_login()
def canvas(request):
    # Get the User object for the currently logged in user
    user, created = FacebookUser.objects.get_or_create(id = request.facebook.uid)

    # Check if we were POSTed the user's new language of choice
    if 'language' in request.POST:
        user.language = request.POST['language'][:64]
        user.save()

    # User is guaranteed to be logged in, so pass canvas.fbml
    # an extra 'fbuser' parameter that is the User object for
    # the currently logged in user.
    return direct_to_template(request, 'fbtest/canvas.fbml', extra_context={'fbuser': user})
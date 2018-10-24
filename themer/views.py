# Create your views here.

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from themer.models import Theme
  
def switch(request, theme_slug):
  """ Sets a cookie to specify the new theme, then redirects to the referer or root url """
  theme = get_object_or_404(Theme, slug=theme_slug)
  referer = "/"
  if "HTTP_REFERER" in request.META:
    referer = request.META["HTTP_REFERER"]
  resp = HttpResponseRedirect(referer)
  resp.set_cookie("theme", theme_slug, 100000)
  return resp
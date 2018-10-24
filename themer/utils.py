from themer.models import Theme

def context_processor(request):
    theme_list = Theme.objects.all()
    if "theme" in request.COOKIES:
        slug = request.COOKIES["theme"]
        try:
            theme = Theme.objects.get(slug=slug)
        except Theme.DoesNotExist:
            theme = None
    else:
        defaults = Theme.objects.filter(is_default=True)
        if defaults.count() > 0:
            theme = defaults[0]
        elif theme_list.count() > 0:
            theme = theme_list[0]
        else:
            theme = None
    return {"current_theme" : theme, "theme_list" : theme_list}


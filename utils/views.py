# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext

def pygments_demo(request, style='default'):
    from pygments.styles import get_all_styles
    from pygments.formatters import HtmlFormatter
    styles = list(get_all_styles())
    html = HtmlFormatter(style=style)
    css = html.get_style_defs('')
    return render_to_response('stuff/pygments_demo.html', locals(), context_instance=RequestContext(request))
"""
For fixing:
1. Nonascii characters in the posts causes an exception
2. Autosave as draft while editing
"""

from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from blog.models import Post

from sitemap import PostsSitemap
from django.contrib.sitemaps import FlatPageSitemap

sitemaps = {
    'blog': PostsSitemap(),
    'pages' : FlatPageSitemap,
}

urlpatterns = patterns('',
    (r'^xd_receiver.htm$', 'django.views.generic.simple.direct_to_template', {'template': 'xd_receiver.htm'}),
    (r'^test.htm$', 'django.views.generic.simple.direct_to_template', {'template': 'test.htm'}),
    (r'^$', 'blog.views.home'),
    (r'^fbtest/$', 'fbtest.views.canvas'),
    (r'^stream/$', 'django.views.generic.simple.direct_to_template', {'template': 'stream.html'}),
    (r'^theme/([a-zA-Z0-9\-]+)/', 'themer.views.switch'),
    (r'^admin/(.*)', admin.site.root),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^xmlrpc/$', 'django_xmlrpc.views.handle_xmlrpc', {}, 'xmlrpc'),
    (r'^pygments/$', 'utils.views.pygments_demo'),
    (r'^pygments/([a-z]+)/$', 'utils.views.pygments_demo'),    
    (r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^', include('blog.urls')),
)

import settings

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'D:\\python\\mysite\\media\\'}),
    )


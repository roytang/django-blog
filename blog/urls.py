from django.conf.urls.defaults import *

from blog.feeds import LatestPosts, LatestComments, LatestPostsByTag

feeds = {
  'posts' : LatestPosts,
  'comments' : LatestComments,
  'tags' : LatestPostsByTag,
}

urlpatterns = patterns('',
  (r'^markdown/preview/$', 'blog.views.markdown_preview'),
  (r'^preview/(\d+)/$', 'blog.views.preview'),
  (r'^random/$', 'blog.views.post_random'),
  (r'^archive/$', 'blog.views.archive'),
  (r'^archive/(\d{4})/(\d{2})/$', 'blog.views.posts_by_month'),
  (r'^([a-zA-Z0-9\-]+)/(\d{4})/(\d{2})/$', 'blog.views.posts_by_cat_month'),
  (r'^search/', 'blog.views.search'),
  (r'^(?P<catslug>[a-zA-Z0-9\-]+)/(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[a-zA-Z0-9\-]+)/$', 'blog.views.post_permalink', {}, 'post_detail'),  
  (r'^tags/$', 'blog.views.tags'),  
  (r'^tags/([a-zA-Z0-9\-_]*)/$', 'blog.views.posts_by_tag'),
  (r'^([a-zA-Z0-9\-]+)/$', 'blog.views.posts_by_category'),
  (r'^feed/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
  (r'^([a-zA-Z0-9\-]+)/feed/$', 'blog.views.category_feed'),
)


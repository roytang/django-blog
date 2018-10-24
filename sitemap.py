from django.contrib.sitemaps import Sitemap
from blog.models import Post

class PostsSitemap(Sitemap):
    changefreq = "never"
    priority = 0.5

    def items(self):
        return Post.pub_objects.all()

    def lastmod(self, obj):
        return obj.last_update_date

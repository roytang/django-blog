from django.contrib.syndication.feeds import Feed
from blog.models import Post, Category
from django.contrib.comments.models import Comment

class LatestPosts(Feed):
    title = "Latest posts on http://roytang.net"
    title_template = 'feeds/post_title.html'
    description_template = 'feeds/post_description.html'
    link = "/"
    description = "Latest posts on http://roytang.net"
    copyright = 'All Rights Reserved'
    author_name = 'Roy Tang'
    
    def items(self):
        return Post.pub_objects.order_by("-date")[:20]

    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        pubdate.
        """
        return item.date
        
class LatestComments(Feed):
    title = "Latest comments on http://roytang.net"
    link = "/"
    description = "Latest comments on http://roytang.net"
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'
    copyright = 'All Rights Reserved'

    def item_link(self, item):
        return item.content_object.get_absolute_url() + "#comments"

    def items(self):
        return Comment.objects.filter(is_removed=False,is_public=True).order_by("-submit_date")[:20]
        
    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's
        pubdate.
        """
        return item.submit_date
        
        
class LatestPostsByCategory(Feed):
    title_template = 'feeds/post_title.html'
    description_template = 'feeds/post_description.html'
    
    def get_object(self, bits):
        if len(bits) < 1:
            raise ObjectDoesNotExist
        return Category.objects.get(slug=bits[0])

    def title(self, obj):
        return "Latest posts under '%s'" % obj.title

    def link(self, obj):
        return "/%s/" % obj.slug

    def description(self, obj):
        return "Latest posts under '%s'" % obj.title

    def items(self, obj):
        return Post.pub_objects.filter(category=obj).order_by("-date")[:20]
  
from tagging.models import Tag, TaggedItem  
class LatestPostsByTag(Feed):
    title_template = 'feeds/post_title.html'
    description_template = 'feeds/post_description.html'
    
    def get_object(self, bits):
        if len(bits) < 1:
            raise ObjectDoesNotExist
        return Tag.objects.get(name=bits[0])

    def title(self, obj):
        return "Latest posts tagged '%s'" % obj.name

    def link(self, obj):
        from django.core.urlresolvers import reverse
        return reverse('blog.views.posts_by_tag', args=[obj.name])

    def description(self, obj):
        return "Latest posts tagged '%s'" % obj.name

    def items(self, obj):
        return TaggedItem.objects.get_by_model(Post, obj).filter(published=True).order_by("-date")[:20]  
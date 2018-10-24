from django.db import models
from tagging.fields import TagField
from tagging.models import Tag
from django.contrib.auth.models import User
from datetime import datetime

class Category(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=250)
    subtitle = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
  
    def __str__(self):
        return self.slug
        
    @models.permalink
    def get_absolute_url(self):
        return ('blog.views.posts_by_category', (self.slug,), {  })        

class PublishedPostManager(models.Manager):
    def get_query_set(self):
        return super(PublishedPostManager, self).get_query_set().filter(published=True, date__lte=datetime.now())
        
class Post(models.Model):
    category = models.ForeignKey(Category)
    author = models.ForeignKey(User)
    date = models.DateTimeField()
    last_update_date = models.DateTimeField()
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    tags = TagField()
    body_markdown = models.TextField('Entry body', help_text='Use Markdown syntax')
    body = models.TextField('Entry body as HTML', blank=True, null=True)
    excerpt = models.TextField(blank=True, null=True)
    use_markdown = models.BooleanField(default=True)
    published = models.BooleanField()
    comments_enabled = models.BooleanField(default=True)
    legacy_id = models.IntegerField(null=True)
    
    objects = models.Manager()
    pub_objects = PublishedPostManager()
    
    def __str__(self):
        return self.title
    
    def comment_count(self):
        from django.contrib.comments.models import Comment
        return Comment.objects.for_model(self).count() 
    
    @models.permalink
    def get_absolute_url(self):
        y = self.date.strftime("%Y")
        m = self.date.strftime("%m")
        return ('blog.views.post_permalink', (self.category.slug, y, m, self.slug), {  })
    
    def get_excerpt(self):
        if self.has_excerpt():
            return self.excerpt
        return self.body
    
    def has_excerpt(self):
        return self.excerpt and self.excerpt != ""
    
    def get_tags(self):
        return Tag.objects.get_for_object(self)        
    
    def save(self):
        # assign the default user as author
        if not self.author_id:
            self.author = User.objects.all()[0]
        if not self.date:
            self.date = datetime.now()
        from blog.utils import autocard, markdown_highlight        
        the_content = self.body_markdown
        the_content = autocard(the_content)
        
        from oembed.core import replace
        the_content = replace(the_content)
        
        #the_content = markdown_highlight(the_content, highlight_only = (not self.use_markdown))
        if self.use_markdown:
            the_content = markdown_highlight(the_content)
        else:
            the_content = markdown_highlight(the_content, highlight_only = True)
        self.body = the_content
        
        self.create_excerpt()

        if self.slug == None or self.slug == "":
            from django.template.defaultfilters import slugify
            self.slug = slugify(self.title)
            
        self.last_update_date = datetime.now()
        super(Post, self).save() # Call the "real" save() method.
        
    def create_excerpt(self):
        """
        >>> p = Post()
        >>> p.body="<p>Para1</p><p>Para2</p>"
        >>> p.create_excerpt()
        >>> p.excerpt
        '<p>Para1</p>'
        >>> p.body="<p>Para1</p><p>Para2</p><!--more--><p>Para3</p>"
        >>> p.create_excerpt()
        >>> p.excerpt
        '<p>Para1</p><p>Para2</p>'
        """
        more = "<!--more-->"
        the_content = self.body
        the_excerpt = ""
        if the_content.find(more) >= 0:
            the_excerpt = the_content[0:the_content.find(more)]
        elif the_content.find("</p>") >= 0:
            the_excerpt = the_content[0:the_content.find("</p>")+4]    
    
        # don't store the excerpt unless absolutely necessary
        if the_excerpt.strip() == the_content.strip():
            self.excerpt = ""
        else:
            self.excerpt = the_excerpt
            
    @property
    def comments_expired(self):
        delta = datetime.now() - self.date
        print delta.days
        return delta.days > 60
            

import settings

# comment moderation
from comment_utils.moderation import CommentModerator, moderator
    
class PostModerator(CommentModerator):
    akismet = True
    email_notification = True
    enable_field = 'comments_enabled'

moderator.register(Post, PostModerator)    

# extra stuff
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

# pingback
from pingback.client import ping_external_links, ping_directories
def should_post_pingback(post):
    if post.published and post.date <= datetime.now():
        return True
    return False
pingbackhandler = ping_external_links(content_attr='body', url_attr='get_absolute_url', filtr=should_post_pingback)

post_save.connect(pingbackhandler, sender=Post)
  

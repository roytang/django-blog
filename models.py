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
    
class Post(models.Model):
  category = models.ForeignKey(Category)
  author = models.ForeignKey(User)
  date = models.DateTimeField()
  title = models.CharField(max_length=250)
  slug = models.SlugField()
  tags = TagField()
  body_markdown = models.TextField('Entry body', help_text='Use Markdown syntax')
  body = models.TextField('Entry body as HTML', blank=True, null=True)
  excerpt = models.TextField(blank=True, null=True)
  use_markdown = models.BooleanField(default=True)
  published = models.BooleanField()
  comments_enabled = models.BooleanField(default=True)
  views = models.IntegerField(default=0)
    
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
    if self.excerpt and self.excerpt != "":
        return "%s<a href='%s'>(More...)</a>" % (self.excerpt, self.get_absolute_url())
    return self.body
    
  def get_tags(self):
    return Tag.objects.get_for_object(self)        
    
  def save(self):
  
    # assign the default user as author
    if not self.author_id:
        self.author = User.objects.all()[0]
        
    if not self.date:
        self.date = datetime.now()
        
    the_content = self.body_markdown
    the_content = autocard(the_content)
    if self.use_markdown:
        the_content = markdown_highlight(the_content)
    self.body = the_content
    
    more = "<!--more-->"
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

    super(Post, self).save() # Call the "real" save() method.


# comment moderation
from comment_utils.moderation import CommentModerator, moderator
    
class PostModerator(CommentModerator):
    akismet = True
    email_notification = True
    enable_field = 'comments_enabled'

#moderator.register(Post, PostModerator)    

# extra stuff
from django.db.models.signals import post_save
from django.db.models.signals import pre_save

# pingback
from pingback.client import ping_external_links, ping_directories
pingbackhandler = ping_external_links(content_attr='body', url_attr='get_absolute_url')
post_save.connect(pingbackhandler, sender=Post)
  

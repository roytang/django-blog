"""
Methods in this file are registered to xmlrpc in __init__.py
"""

"""
Pingback stuff
"""

from datetime import time, date, datetime
from time import strptime

from blog.models import Post, Category
from pingback import create_ping_func
from django_xmlrpc import xmlrpcdispatcher

# create simple function which returns Post object and accepts
# exactly same arguments as 'details' view.
def pingback_blog_handler(catslug, year, month, slug, **kwargs):
    cat = Category.objects.get(slug=catslug)
    return Post.pub_objects.get(date__year=year, date__month=month, slug=slug, category=cat, published=True)
    
# define association between view name and our handler
ping_details = {'post_detail': pingback_blog_handler}

# create xml rpc method, which will process all
# ping requests
ping_func = create_ping_func(**ping_details)


"""
Metaweblog stuff follows
"""

from django.contrib.auth.models import User
import settings

def authenticated(pos=1):
    """
    A decorator for functions that require authentication.
    Assumes that the username & password are the second & third parameters.
    Doesn't perform real authorization (yet), it just checks that the
    user is_superuser.
    """
    
    def _decorate(func):
        def _wrapper(*args, **kwargs):
            print "wrapper"
            username = args[pos+0]
            password = args[pos+1]
            args = args[0:pos]+args[pos+2:]
            try:
                user = User.objects.get(username__exact=username)
            except User.DoesNotExist:
                raise ValueError("Authentication Failure")
            if not user.check_password(password):
                raise ValueError("Authentication Failure")
            if not user.is_superuser:
                raise ValueError("Authorization Failure")
            return func(user, *args, **kwargs)
        
        return _wrapper
    return _decorate
    
@authenticated()
def blogger_getUsersBlogs(user, appkey):
    """
    an array of <struct>'s containing the ID (blogid), name
    (blogName), and URL (url) of each blog.
    """
    return [{
            'blogid': settings.SITE_ID,
            'blogName': 'Roy Tang',
            'url': settings.SITE_URL
            }]
            
@authenticated()
def metaWeblog_getCategories(user, blogid):
    catlist = Category.objects.all()
    return [{'description':cat.title,'htmlUrl':cat.get_absolute_url(),'rssUrl':''} for cat in catlist]
    
from datetime import datetime

def setCategory(post, struct):
    category_list = struct.get('categories', None)
    if category_list is None or len(category_list) == 0:
        post.category = Category.objects.get(slug='blog')
    else:
        post.category = Category.objects.get(title=category_list[0])

def sliceTags(body):
    """
    Parse the body tag posted and strip out technorati tags
    """
    from BeautifulSoup import BeautifulSoup   
    
    soup = BeautifulSoup(body)
    tags = []
    anchors = soup.findAll("a")
    for anchor in anchors:
        try:
            if anchor["rel"] == "tag":
                from django.template.defaultfilters import slugify
                tag = slugify("%s" % anchor.string)
                tags.append(tag)
                anchor.replaceWith("")
        except KeyError:
            continue
    
    return body, ",".join(tags)
          
@authenticated()
def metaWeblog_newPost(user, blogid, struct, publish):
    post = Post()
    post.title = struct['title']
    body = struct['description']
    if body is not None:
        body, tags = sliceTags(body)
        post.body_markdown = body
        post.tags = tags
    post.use_markdown = True
    post.published = publish
    post.date = datetime.now()
    post.author = user
    setCategory(post, struct)
    post.save()
    return post.id 

import urlparse
def full_url(url):
    return urlparse.urljoin(settings.SITE_URL, url)

from xmlrpclib import DateTime
  
def format_date(d):
    if not d: return None
    return DateTime(d.isoformat())
    
def post_struct(post):
    link = full_url(post.get_absolute_url())
    struct = {
        'postid': post.id,
        'title': post.title,
        'link': link,
        'permaLink': link,
        'description': post.body,
        'categories': post.category.title,
        'userid': post.author.id,
        }
    if post.published:
        struct['dateCreated'] = format_date(post.date)
    return struct
    
@authenticated()
def metaWeblog_getPost(user, postid):
    post = Post.objects.get(id=postid)
    return post_struct(post)


@authenticated()
def metaWeblog_getRecentPosts(user, blogid, num_posts):
    posts = Post.pub_objects.order_by('-date')[:int(num_posts)]
    return [post_struct(post) for post in posts]    
    
@authenticated()
def metaWeblog_editPost(user, postid, struct, publish):
    post = Post.objects.get(id=postid)
    title = struct.get('title', None)
    if title is not None:
        post.title = title
    body = struct.get('description', None)
    if body is not None:
        body, tags = sliceTags(body)
        post.body_markdown = body
        post.tags = tags
    if user:
        post.author = user
    post.published = publish
    setCategory(post, struct)
    post.save()
    return True    
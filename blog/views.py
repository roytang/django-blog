# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.date_based import archive_month
from django.http import Http404
from django.template import RequestContext

from datetime import datetime
from blog.forms import PostForm
from blog.models import Post, Category
  
def home(request):
  """ Like a normal post object list, except we provide the category_list in the context as well """
  queryset = Post.pub_objects.order_by("-date")
  paginate_by = 5
  category_list = Category.objects.all()
  return object_list(request, queryset, paginate_by, 
    template_name="home.html", 
    extra_context = { "request" : request, "category_list" : category_list}
	)
  
@login_required  
def preview(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render_to_response("blog/post_detail.html", locals(), context_instance=RequestContext(request)) 
    
def posts_by_category(request, catslug):
    cat = get_object_or_404(Category, slug=catslug)
  
    # support legacy wordpress style "p" queries
    if ('p' in request.GET) and request.GET['p'].strip():
        try:
            p = int(request.GET['p'])
            posts = Post.pub_objects.filter(legacy_id=p, category=cat)
            if len(posts) == 0:
                # if none found, check other categories
                posts = Post.pub_objects.filter(legacy_id=p)
            
            # just get the first post matched
            if len(posts) >= 1:
                post = posts[0]
            else:
                raise Http404
            return HttpResponseRedirect(post.get_absolute_url())
        except ValueError:
            pass # just process as a normal category
        
    queryset = Post.pub_objects.filter(category=cat).order_by('-date')
    return object_list(request, queryset, paginate_by=5, 
        template_name="blog/by_category.html", 
        extra_context={ "request" : request, "category":cat, "count":queryset.count()})    
  
def post_permalink(request, catslug, year, month, slug):
    cat = get_object_or_404(Category, slug=catslug)
    year = int(year)
    month = int(month)
    post = get_object_or_404(Post, date__year=year, date__month=month, slug=slug, category=cat, published=True, date__lte=datetime.now())
    return render_to_response("blog/post_detail.html", locals(), context_instance=RequestContext(request)) 
    
def post_random(request):
    post = Post.pub_objects.order_by('?')[0]
    return HttpResponseRedirect(post.get_absolute_url())
  
from tagging.models import Tag, TaggedItem
from django.views.generic.list_detail import object_list

def posts_by_tag(request, tag):
  o_tag = Tag.objects.get(name=tag)
  queryset = TaggedItem.objects.get_by_model(Post, o_tag).filter(published=True).order_by("-date")
  return object_list(request, queryset, paginate_by=5, 
    template_name="blog/by_tag.html", 
    extra_context={ "request" : request, "tag":tag, "count":queryset.count()})    

from datetime import datetime  
def posts_by_month(request, year, month):  
  date = datetime(int(year), int(month), 1)
  queryset = Post.pub_objects.filter(date__year=int(year),date__month=int(month)).order_by('-date')  
  return object_list(request, queryset, paginate_by=5, 
    template_name="blog/by_month.html", 
    extra_context={ "request" : request, "count":queryset.count(), "date":date})    
 
def posts_by_cat_month(request, catslug, year, month):  
  cat = get_object_or_404(Category, slug=catslug)
  date = datetime(int(year), int(month), 1)
  queryset = Post.pub_objects.filter(category=cat,date__year=int(year),date__month=int(month)).order_by('-date')  
  return object_list(request, queryset, paginate_by=5, 
    template_name="blog/by_cat_month.html", 
    extra_context={ "request" : request, "count":queryset.count(), "date":date, "category":cat})    
 
def tags(request):
    tag_cloud = Tag.objects.cloud_for_model(Post)
    count = len(tag_cloud)
    return render_to_response("blog/tags.html", locals(), context_instance=RequestContext(request))
    
def archive(request):
    years = Post.pub_objects.dates('date', 'year', order='DESC')
    archives = []
    for year in years:
        month_list = Post.pub_objects.filter(date__year=year.year).dates('date', 'month')
        months = []
        for month in month_list:
            count = Post.pub_objects.filter(date__year=year.year,date__month=month.month).count()
            months.append( { "month":month, "count": count } )
        archives.append( { "year":year, "months":months } )
    return render_to_response("blog/archive.html", locals(), context_instance=RequestContext(request))  

def markdown_preview(request):
    processed = ''
    if request.method == 'POST':
        from blog.utils import autocard, markdown_highlight  
        processed = request.POST.get('data')
        processed = autocard(processed)
        processed = markdown_highlight(processed)
    return HttpResponse(processed)        
    
from django.contrib.syndication.views import feed    
from blog.feeds import LatestPostsByCategory

def category_feed(request, catslug):
    feeds = {
        'category' : LatestPostsByCategory,
    }
    url = "category/%s/" % catslug
    return feed(request, url, feed_dict=feeds)

    
# http://www.djangosnippets.org/snippets/1211/  
import re
from django.db.models import Q
from django.template import RequestContext

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search(request):
    query_string = ''
    found_entries = None
    count = 0
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = get_query(query_string, ['title', 'body',])
        found_entries = Post.pub_objects.filter(entry_query).order_by('-date')
        count = found_entries.count()

    return render_to_response('blog/search_result.html',
                          { 'count' : count, 'query_string': query_string, 
                            'object_list': found_entries, "request":request },
                          context_instance=RequestContext(request))
                          

        
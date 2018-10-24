from django.contrib import admin
from blog.models import Post, Category
from django import forms
from django.utils import simplejson
from django.utils.safestring import mark_safe
from tagging.models import Tag
from tagging.forms import TagField

class AutoCompleteTagInput(forms.TextInput):
    class Media:
        css = {
            'all': ('/files/css/jquery.autocomplete.css',)
        }
        js = (
            '/files/js/jquery.js',
            '/files/js/lib/jquery.bgiframe.min.js',
            '/files/js/lib/jquery.ajaxQueue.js',
            '/files/js/jquery.autocomplete.min.js'
        )

    def render(self, name, value, attrs=None):
        output = super(AutoCompleteTagInput, self).render(name, value, attrs)
        page_tags = Tag.objects.usage_for_model(Post)
        tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                    ensure_ascii=False)
        return output + mark_safe(u'''<script type="text/javascript">
            jQuery("#id_%s").autocomplete(%s, {
                width: 150,
                max: 10,
                highlight: false,
                multiple: true,
                multipleSeparator: ", ",
                scroll: true,
                scrollHeight: 300,
                matchContains: true,
                autoFill: true,
            });
            </script>''' % (name, tag_list))

class MarkItUpWidget(forms.Textarea):
    class Media:
        js = (
            '/files/js/jquery.js',
            '/files/js/markitup/jquery.markitup.js',
            '/files/js/markitup/sets/markdown/set.js',
            '/files/js/markitup_postadmin.js',
        )
        css = {
            'screen': (
                '/files/js/markitup/skins/simple/style.css',
                '/files/js/markitup/sets/markdown/style.css',
            )
        }

class PostAdminForm(forms.ModelForm):
    body_markdown = forms.CharField(widget=MarkItUpWidget())
    tags = TagField(widget=AutoCompleteTagInput(), required=False)

    class Meta:
        model = Post
        
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}
    date_hierarchy = 'date'
    list_display = [ 'date', 'title', 'author', 'tags', 'comment_count', 'published' ]
    list_display_links = [ 'title' ]
    list_filter = ('published', 'date')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'body_markdown', 'category', 'tags', 'use_markdown', 'published')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('comments_enabled', 'excerpt')
        }),
    )
    radio_fields = { "category" : admin.HORIZONTAL }
    form = PostAdminForm

    def save_model(self, request, obj, form, change): 
        instance = form.save(commit=False)
        if not instance.author_id:
            instance.user = request.user

        instance.save()
        return instance


class CategoryAdmin(admin.ModelAdmin):
    list_display = [ 'slug', 'title' ]
    
admin.site.register(Post,PostAdmin)	
admin.site.register(Category, CategoryAdmin)	

from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
import settings

class CustomFlatPageAdmin(FlatPageAdmin):
    class Media:
        js = ("http://js.nicedit.com/nicEdit-latest.js", "/files/js/nicEdit-init.js",)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, CustomFlatPageAdmin)	

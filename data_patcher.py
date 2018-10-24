"""
This data patch imports the legacy_id
"""

from blog.models import Post, Category
from tagging.models import Tag, TaggedItem

from django.contrib.auth.models import User
from datetime import datetime
from html2text import html2text
from django.contrib.comments.models import Comment
from pingback.models import Pingback
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType

def nvls(str0):
  if str0 == None:
    return ""
  return str0

import re
from BeautifulSoup import BeautifulSoup

def do_patch(xml):
  f = open(xml).read()
  f = f.replace("<wp:", "<").replace("</wp:", "</")
  f = f.replace("<content:encoded", "<content").replace("</content:encoded", "</content")
  f = f.replace("<excerpt:encoded", "<excerpt").replace("</excerpt:encoded", "</excerpt")
  from BeautifulSoup import BeautifulStoneSoup
  s = BeautifulStoneSoup(f)
  site = Site.objects.get()
  
  for item in s.findAll('item'):
    if item.post_type.string == "post":
      d = datetime.strptime(item.pubdate.string, "%a, %d %b %Y %H:%M:%S +0000")
      slug = nvls(item.post_name.string)
      if len(slug) > 50:
        slug = slug[0:50]
      legacy_id = nvls(item.post_id.string)
      print "%s, %s, %s\n" % (str(d), slug, legacy_id)
      matches = Post.objects.filter(slug=slug, date=d)
      if len(matches) > 1:
        print "WARN: More than one match for legacy id %s" % legacy_id
        continue
      if len(matches) == 0:
        print "WARN: No matches for legacy id %s" % legacy_id
        continue
      p = matches[0]
      p.legacy_id = legacy_id
      p.save()
  
if __name__ == "__main__":
    do_patch("./magic.xml")

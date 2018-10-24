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

def replace_wp_upload_link(link):
    if link and link != "":
        link = link.replace("http://roytang.net/blog/wp-content", "/files")
        link = link.replace("http://roytang.net/magic/wp-content", "/files")
    return link
    
def replace_wp_uploads(content):
    """
    Map http://roytang.net/blog/wp-content/uploads/2008/08/badcombo.jpg
    to /files/uploads/2008/08/badcombo.jpg    
    """
    soup = BeautifulSoup(content)
    anchors = soup.findAll("a")
    for anchor in anchors:
        anchor["href"] = replace_wp_upload_link(anchor["href"])
    images = soup.findAll("img")
    for image in images:
        image["src"] = replace_wp_upload_link(image["src"])
    
    return soup.prettify()

def auto_pee(content):
    """Convert double-newlines into <p></p> pairs"""
    STARTP = "UNIQUESTRINGOPENP"
    ENDP = "UNIQUESTRINGCLOSINGP"
    
    # cleanup autocard
    content = content.replace("[CARD]", "<card>")
    content = content.replace("[/CARD]", "</card>")
    content = content.replace("[DECK]", "<deck>")
    content = content.replace("[/DECK]", "</deck>")    
    
    # First, pull out all the block-level blocks, to keep them safe
    soup = BeautifulSoup(content)
    blocks = {}
    allblocks = "deck|ul|ol|li|table|thead|tfoot|caption|colgroup|tbody|tr|td|th|div|dl|dd|dt|pre|select|form|map|area|blockquote|address|math|style|input|p|h1|h2|h3|h4|h5|h6|hr".split("|")
    for block in allblocks:
        my_blocks = soup.findAll(block)
        for a_block in my_blocks:
            a_block.replaceWith(ENDP + '<%s class="removed"></%s>' % (block, block) + STARTP)
        blocks[block] = my_blocks

    new_content =  str(soup)
    if new_content.startswith(ENDP):
        new_content = new_content[len(ENDP):]
    if new_content.endswith(STARTP):
        new_content = new_content[0: -1*len(STARTP)]
    new_content =  "<p>" + new_content + "</p>"
    new_content = re.sub("\n\n+", "\n\n", new_content)
    new_content = new_content.replace("\n\n", "</p><p>")
    new_content = new_content.replace("\n", "<br/>")

    # Restore the removed blocks
    allblocks.reverse()
    for block in allblocks:
        soup = BeautifulSoup(new_content)
        if block in blocks:
            my_blocks = blocks[block]
            empty_blocks, index = soup.findAll(block, 'removed'), 0
            for a_block in my_blocks:
                empty_blocks[index].replaceWith(a_block)
                index = index + 1
        new_content = str(soup)

    retval = soup.prettify()
    retval = retval.replace(ENDP, "</p>")
    retval = retval.replace(STARTP, "<p>")
    
    return retval
    
def do_import(xml, cat):
  f = open(xml).read()
  f = f.replace("<wp:", "<").replace("</wp:", "</")
  f = f.replace("<content:encoded", "<content").replace("</content:encoded", "</content")
  f = f.replace("<excerpt:encoded", "<excerpt").replace("</excerpt:encoded", "</excerpt")
  from BeautifulSoup import BeautifulStoneSoup
  s = BeautifulStoneSoup(f)
  user = User.objects.get()
  site = Site.objects.get()
  
  post_count = 0
  cmt_count = 0
  cat = Category.objects.get(slug=cat)
  
  for item in s.findAll('item'):
    if item.post_type.string == "post":
      p = Post()
      p.category = cat
      p.title = item.title.string
      print p.title
      p.author = user
      d = datetime.strptime(item.pubdate.string, "%a, %d %b %Y %H:%M:%S +0000")
      p.date = d
      the_content = nvls(item.content.string)
      try:
        the_content = auto_pee(the_content)      #p.body_markdown = html2text(the_content)
      except:
        print "Autopee for %s failed, copying as-is" % p.title
        the_content = nvls(item.content.string)
        
      the_content = replace_wp_uploads(the_content)
      
      p.body_markdown = the_content
      p.slug = nvls(item.post_name.string)
      if len(p.slug) > 50:
        p.slug = p.slug[0:50]
      if item.status.string == 'publish':
        p.published = True
      
      p.use_markdown = False
      p.save()
      #print item('category')[1]['nicename']
      tags = []
      for tag in item.findAll('category'):
        try:
          tagname = tag["nicename"]          
          if tagname not in tags:
            tags.append(tagname)
          #print tagname
        except KeyError:
          pass
        p.tags = " ".join(tags)
        p.save()
      post_count = post_count + 1
      for cmt in item.findAll('comment'):
        if cmt.comment_approved.string == "spam":
            continue
            
        the_content = cmt.comment_content.string.replace("\n", "<br />")
        the_content = html2text(the_content)
        d = datetime.strptime(cmt.comment_date.string, "%Y-%m-%d %H:%M:%S")
        url = nvls(cmt.comment_author_url.string)
        name = "%s" % cmt.comment_author.string
        if cmt.comment_type.string == "pingback":
            if len(name) > 100:
                name = name[0:100]
            pb = Pingback(object=p, url=url, content=the_content, title=name, approved=True)
            pb.date = d
            pb.save()            
            continue
        c = Comment()
        c.object_pk = p.id
        c.site = site
        c.user_name = name
        c.user_email = cmt.comment_author_email.string
        if c.user_email == None:
          c.user_email = ""
        c.user_url = url
        c.ip_address = cmt.comment_author_ip.string
        c.is_public = True
        c.is_removed = False
        c.comment = the_content
        c.submit_date = d
        c.content_type = ContentType.objects.get_for_model(p)
        c.save()
        cmt_count = cmt_count + 1
#      if post_count > 50:
#        break
  print "%s posts, %s comments imported" % (str(post_count), str(cmt_count))
  
#do_import("d:\\test.xml", "blog")

def category_init_data():
    if Category.objects.all().count() > 0:
        return
    c = Category()
    c.slug = 'blog'
    c.title = 'Stuff'
    c.subtitle = 'Programmer, engineer, scientist, critic, gamer, dreamer, and kid-at-heart'
    c.description = 'Everyday things, random encounters and slices of life.'
    c.save()
    c = Category()
    c.slug = 'dev'
    c.title = 'Software Development'
    c.subtitle = 'Software Development'
    c.description = 'I work as a technical lead for an HK-based software shop. I code using Java, .Net and Python.'
    c.save()
    c = Category()
    c.slug = 'magic'
    c.title = 'Magic the Gathering'
    c.subtitle = 'Making the bad plays so you don''t have to'
    c.description = 'I''m a longtime Magic: the Gathering  player from the Philippines looking to make his mark on the competitive scene. Follow along on his journey by  reading his tournament reports and  insights on the game.'
    c.save()
    c = Category()
    c.slug = 'games'
    c.title = 'Gaming'
    c.subtitle = 'Because life is a game'
    c.description = 'I play real-life, video and computer games. A lot.'
    c.save()
    
    

def migrate_tag_to_category(tag, category):
    c = Category.objects.filter(slug=category)[0]
    t = Tag.objects.get(name=tag)
    q = TaggedItem.objects.get_by_model(Post, t)
    for p in q:
        if p.category != c:
            print p.title
            p.category = c
            p.save()

def test():
    while Post.objects.all().count() > 0:
        Post.objects.all()[0].delete()
    do_import("./test.xml", "magic")  

if __name__ == "__main__":
    category_init_data()
    do_import("./main.xml", "blog")  
    do_import("./magic.xml", "magic")
    do_import("./django.xml", "dev")
    migrate_tag_to_category("developer", "dev")
    migrate_tag_to_category("games", "games")

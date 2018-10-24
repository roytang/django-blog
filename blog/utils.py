from blog.models import Category

def context_processor(request):
    category_list = Category.objects.all()
    return {"category_list" : category_list}

# BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
from BeautifulSoup import BeautifulSoup     

from django.template.loader import render_to_string
   
import re    
def autocard(content):
    """Render this content for display."""
    
    if content.find("<card") < 0 and content.find("<deck") < 0:
        return content
        
    soup = BeautifulSoup(content)
    card_blocks = soup.findAll('card')
    for block in card_blocks:
        card_name = block.string
        if card_name and card_name != "":
            block.replaceWith(autocard_link(card_name))
    deck_blocks = soup.findAll('deck')
    for block in deck_blocks:
        try:
            MAX_COLS = int(block["cols"])
        except KeyError:
            MAX_COLS = 3
        if block.string:
            list_for_parsing = block.string
        else:
            child_tags = block.findAll()
            list_for_parsing = ""
            for tag in child_tags:
                if tag.string:
                    list_for_parsing = list_for_parsing + "\n" + tag.string + "\n"
        lines = list_for_parsing.split("\n")
        new_deck = ""
        groups = []
        new_group = { 'title' : '', 'cards' : [] }
        for line in lines:
            header = True
            line = line.strip()
            if line == "":
                continue
            if re.match('(\d+)', line):
                count = re.sub(
                             '(\d+)(\s*)([^\<]*)', 
                             '\g<1>', 
                             line)
                name = re.sub(
                             '(\d+)(\s*)([^\<]*)', 
                             '\g<3>', 
                             line)
                new_group['cards'].append({ 'count' : int(count), 'name' : name })
                header = False
            if header:
                # end the previous group
                if len(new_group['cards']) > 0:
                    groups.append(new_group)
                #new_deck = new_deck + "<ul class='decklist_group'>%s</ul>" % new_group
                new_group = { 'title' : line, 'cards' : [] }
            #new_group = new_group + "<li%s>%s</li>\n" % (cls, line)
        # end the previous group
        if len(new_group['cards']) > 0:
            groups.append(new_group)
        groups_per_col = len(groups)/MAX_COLS
        cols = []
        col = []
        for group in groups:
            if len(col) >= groups_per_col and len(cols) < MAX_COLS - 1:
                cols.append(col)
                col = []
            col.append(group)
        cols.append(col)
        block.replaceWith(render_to_string('autocard/deck.html', { 'cols' : cols }))
    
    #print str(soup)
    return str(soup)
    
def autocard_link(card_name):
    if card_name:
        card_name = card_name.strip()
        return render_to_string('autocard/card.html', { 'name' : card_name })
    return card_name
            
    
# Pygments: http://pygments.org -- a generic syntax highlighter.
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

from markdown2 import markdown
    
def markdown_highlight(content, safe="unsafe", highlight_only=False):
    """Render this content for display."""

    # First, pull out all the <code></code> blocks, to keep them away
    # from Markdown (and preserve whitespace).
    soup = BeautifulSoup(content)
    code_blocks = soup.findAll('code')
    for block in code_blocks:
        block.replaceWith('<code class="removed"></code>')
    new_content = str(soup)
    
    # Run the post through markdown.
    if not highlight_only:
        if safe == "unsafe":
            safe_mode = False
        else:
            safe_mode = True
        new_content = markdown(new_content, safe_mode=safe_mode)
        # Replace the pulled code blocks with syntax-highlighted versions.
        
    soup = BeautifulSoup(new_content)
    empty_code_blocks, index = soup.findAll('code', 'removed'), 0
    formatter = HtmlFormatter(cssclass='source', linenos='table')
    for block in code_blocks:
        if block.has_key('class'):
            # <code class='python'>python code</code>
            language = block['class']
        else:
            # <code>plain text, whitespace-preserved</code>
            language = 'text'
        try:
            lexer = get_lexer_by_name(language, stripnl=True, encoding='UTF-8')
        except ValueError, e:
            try:
                # Guess a lexer by the contents of the block.
                lexer = guess_lexer(block.renderContents())
            except ValueError, e:
                # Just make it plain text.
                lexer = get_lexer_by_name('text', stripnl=True, encoding='UTF-8')
        empty_code_blocks[index].replaceWith(
                "<div class='hl_wrap'>%s</div>" % highlight(block.renderContents(), lexer, formatter))
        index = index + 1
    
    return str(soup)
    
def auto_pee(content):
    """Convert double-newlines into <p></p> pairs"""
    STARTP = "UNIQUESTRINGOPENP"
    ENDP = "UNIQUESTRINGCLOSINGP"
    
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
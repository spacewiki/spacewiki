import bleach
from flask import url_for
import model
import peewee
import re

TAG_WHITELIST = [
    'ul', 'li', 'ol', 'p', 'table', 'div', 'tr', 'th', 'td', 'em', 'big', 'b',
    'strong', 'a', 'abbr', 'aside', 'audio', 'blockquote', 'br', 'button', 'code',
    'dd', 'del', 'dfn', 'dl', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i',
    'img', 'ins', 'kbd', 'pre', 's', 'small', 'span', 'sub', 'sup', 'u',
    'video', 'section', 'input', 'form'
]

ATTRIBUTE_WHITELIST = {
    '*': ['style', 'class', 'id', 'tabindex', 'name'],
    'a': ['href'],
    'img': ['src', 'alt'],
    'form': ['action', 'method'],
    'input': ['type', 'placeholder', 'value'],
}

STYLE_WHITELIST = [
    'margin', 'text-align', 'font-weight', 'size', 'color', 'background-color',
    'padding', 'border', 'line-height', 'padding-top', 'float', 'margin-left',
    'position'
]

TEMPLATE_SYNTAX = re.compile(r'\{\{(.+?)\}\}')
LINK_SYNTAX = re.compile(r'\[\[(.+?)\]\]')
TITLED_LINK_SYNTAX = re.compile(r'\[\[(.+?)\|(.+?)\]\]')

def safetags(s):
    """Strips out everything that isn't a whitelisted HTML tag"""
    return bleach.clean(s, attributes=ATTRIBUTE_WHITELIST,
        tags=TAG_WHITELIST, styles=STYLE_WHITELIST, strip_comments=False)

def do_attachment(pageSlug, slug):
    print "attachment", slug
    size = None
    try:
        imageSlug, size = slug.split(':', 1)
    except Exception, e:
        imageSlug = slug
    try:
        attachment = model.Attachment.get(slug=imageSlug)
    except peewee.DoesNotExist:
        return None
    if size is None:
        imgUrl = url_for('uploads.get_attachment', slug=pageSlug, fileslug=imageSlug)
    else:
        imgUrl = url_for('uploads.get_attachment', slug=pageSlug, fileslug=imageSlug,
            size=size)
    fullUrl = url_for('uploads.get_attachment', slug=pageSlug, fileslug=imageSlug)
        
    return '[![%s](%s)](%s)'%(imageSlug, imgUrl, fullUrl)

def do_template(match, pageSlug, depth):
    """Replaces a template regex match with the template contents,
    recursively"""
    slug = match.groups()[0]
    if depth > 10:
        return "{{Max include depth of %s reached before [[%s]]}}"%(depth, slug)
    if slug.startswith("attachment:"):
        imageSlug = slug.split(':', 1)[1]
        return do_attachment(pageSlug, imageSlug)
    else:
        replacement = model.Page.latestRevision(slug)
    if replacement is None:
        return "{{[[%s]]}}"%(slug)
    return wikitemplates(replacement.body, pageSlug, depth=depth+1)

def wikitemplates(s, pageSlug, depth=0):
    def do_template_with_depth(*args): #pylint: disable=missing-docstring
        return do_template(*args, pageSlug=pageSlug, depth=depth)
    return TEMPLATE_SYNTAX.sub(do_template_with_depth, s)

def make_wikilink(match):
    groups = match.groups()
    if len(groups) == 1:
        title = groups[0]
        link = groups[0]
    else:
        title = groups[1]
        link = groups[0]
    link = model.SlugField.slugify(link)
    if model.Page.select().where(model.Page.slug == link).exists():
        return "[%s](%s)"%(title, link)
    else:
        return "[%s<sup>?</sup>](%s)"%(title, link)

def wikilinks(s):
    s = TITLED_LINK_SYNTAX.sub(make_wikilink, s)
    s = LINK_SYNTAX.sub(make_wikilink, s)
    return s

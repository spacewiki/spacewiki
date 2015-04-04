import bleach
import model
import re

tag_whitelist = [
  'ul', 'li', 'ol', 'p', 'table', 'div', 'tr', 'th', 'td', 'em', 'big', 'b',
  'strong', 'a', 'abbr', 'aside', 'audio', 'blockquote', 'br', 'button', 'code',
  'dd', 'del', 'dfn', 'dl', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i',
  'img', 'ins', 'kbd', 'pre', 's', 'small', 'span', 'sub', 'sup', 'u', 'video'
]

templateSyntax = re.compile("\{\{(.+?)\}\}")
linkSyntax = re.compile("\[\[(.+?)\]\]")
titledLinkSyntax = re.compile("\[\[(.+?)\|(.+?)\]\]")

def init(app):
    @app.template_filter('safetags')
    def safetags(s):
        return bleach.clean(s, tags=tag_whitelist, strip_comments=False)

    def do_template(match, depth):
        slug = match.groups()[0]
        if depth > 10:
          return "{{Max include depth of %s reached before [[%s]]}}"%(depth, slug)
        replacement = model.Page.latestRevision(slug)
        if replacement is None:
            return "{{[[%s]]}}"%(slug)
        return wikitemplates(replacement.body, depth=depth+1)

    @app.template_filter('wikitemplates')
    def wikitemplates(s, depth=0):
        def r(*args):
          return do_template(*args, depth=depth)
        return templateSyntax.sub(r, s)

    def make_wikilink(match):
        groups = match.groups()
        if len(groups) == 1:
            title = groups[0]
            link = groups[0]
        else:
            title = groups[1]
            link = groups[0]
        return "[%s](%s)"%(title, link)

    @app.template_filter('wikilinks')
    def wikilinks(s):
        s = titledLinkSyntax.sub(make_wikilink, s)
        s = linkSyntax.sub(make_wikilink, s)
        return s


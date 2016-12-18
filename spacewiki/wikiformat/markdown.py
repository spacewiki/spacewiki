"""Markdown portion of wikitext implementation"""

import mistune
import re
import unfurl

class WikiRenderer(mistune.Renderer):
    """Specialization of markdown renderer that handles wiki format additions"""
    def block_html(self, html):
        tokens = html.split('\n', 1)
        if len(tokens) == 2:
            first_line, rest = html.split('\n', 1)
        else:
            first_line = html
            rest = ""
        tags = re.match('^<(.+?)>(.*)', html)
        renderer = WikiRenderer()
        parser = mistune.Markdown(renderer=renderer)
        if tags:
            tag, tag_tail = tags.groups()
            rest = tag_tail + rest
            submd = parser.render(unicode(rest))
            ret = "<%s>%s" % (tag, submd)
        else:
            ret = first_line + parser.render(unicode(rest.lstrip()))
        return ret

    def autolink(self, link, is_email=False):
        return unfurl.unfurl_url(link)


def render(text):
    """Renders a string of markdown text as HTML"""
    renderer = WikiRenderer()
    parser = mistune.Markdown(renderer=renderer)
    return parser.render(text)

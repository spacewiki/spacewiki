"""Implementation of SpaceWiki's wikitext syntax"""
import bleach
from flask import url_for
import peewee
import re

from . import links, directives, markdown

TAG_WHITELIST = [
    'ul', 'li', 'ol', 'p', 'table', 'div', 'tr', 'th', 'td', 'em', 'big', 'b',
    'strong', 'a', 'abbr', 'aside', 'audio', 'blockquote', 'br', 'button',
    'code', 'dd', 'del', 'dfn', 'dl', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'hr', 'i', 'img', 'ins', 'kbd', 'pre', 's', 'small', 'span', 'sub', 'sup',
    'u', 'video', 'section', 'input', 'form'
]

ATTRIBUTE_WHITELIST = {
    '*': ['style', 'class', 'id', 'tabindex', 'name'],
    'td': ['colspan', 'rowspan'],
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

def safetags(text):
    """Strips out everything that isn't a whitelisted HTML tag"""
    return bleach.clean(text, attributes=ATTRIBUTE_WHITELIST,
                        tags=TAG_WHITELIST, styles=STYLE_WHITELIST,
                        strip_comments=False)


def render_wikitext(text, slug):
    """Renders a string of wikitext as HTML"""
    return safetags(markdown.render(links.render(directives.render(text, slug))))


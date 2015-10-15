"""Implementation of wiki links in SpaceWiki's wikitext"""
import re
import flask

from spacewiki import model

LINK_SYNTAX = re.compile(r'\[\[(.+?)\]\]')
TITLED_LINK_SYNTAX = re.compile(r'\[\[(.+?)\|(.+?)\]\]')


def make_wikilink(match):
    """Regex callback to process a wikilink into markdown"""
    groups = match.groups()
    if len(groups) == 1:
        title = groups[0]
        link = groups[0]
    else:
        title = groups[1]
        link = groups[0]
    link = model.SlugField.slugify(link)
    if model.Page.select().where(model.Page.slug == link).exists():
        return "[%s](%s)" % (title, flask.url_for('pages.view', slug=link))
    else:
        return "[%s<sup>?</sup>](%s)" % (title, flask.url_for('pages.view', slug=link))


def render(text):
    """Parses text for wikitext links and renders them as markdown"""
    text = TITLED_LINK_SYNTAX.sub(make_wikilink, text)
    text = LINK_SYNTAX.sub(make_wikilink, text)
    return text

"""Implements {{directives}} in wikitext"""

from flask import url_for
import peewee
import re

from spacewiki import model

DIRECTIVE_SYNTAX = re.compile(r'\{\{(.+?)\}\}')

def do_attachment(pageSlug, slug):
    size = None

    tokens = slug.split(':', 1)

    if len(tokens) == 1:
        image_slug = slug
    else:
        image_slug, size = tokens

    try:
        model.Attachment.get(slug=image_slug)
    except peewee.DoesNotExist:
        # FIXME: Return markdown that indicates this attachment doesn't exist
        return None

    if size is None:
        img_url = url_for('uploads.get_attachment',
                          slug=pageSlug, fileslug=image_slug)
    else:
        img_url = url_for('uploads.get_attachment',
                          slug=pageSlug, fileslug=image_slug, size=size)

    full_url = url_for('uploads.get_attachment',
                       slug=pageSlug, fileslug=image_slug)

    return '[![%s](%s)](%s)' % (image_slug, img_url, full_url)


def do_template(match, pageSlug, depth):
    """Replaces a template regex match with the template contents,
    recursively"""
    slug = match.groups()[0]
    if depth > 10:
        return "{{Max include depth of %s reached before [[%s]]}}" % (
            depth, slug
        )
    if slug.startswith("attachment:"):
        image_slug = slug.split(':', 1)[1]
        return do_attachment(pageSlug, image_slug)
    else:
        replacement = model.Page.latestRevision(slug)
    if replacement is None:
        return "{{[[%s]]}}" % (slug,)
    return render(replacement.body, pageSlug, depth=depth+1)


def render(s, pageSlug, depth=0):
    def do_template_with_depth(*args):  # pylint: disable=missing-docstring
        return do_template(*args, pageSlug=pageSlug, depth=depth)

    return DIRECTIVE_SYNTAX.sub(do_template_with_depth, s)

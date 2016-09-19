"""Routes to handle the realtime editor"""

from flask import (Blueprint, current_app, render_template, request, redirect,
        url_for)
from spacewiki import model
import peewee

import logging
BLUEPRINT = Blueprint('editor', __name__)

@BLUEPRINT.route("/preview", methods=['POST'])
def preview():
    """Render some markup as HTML"""
    return model.Revision.render_text(request.form['body'],
                                      request.form['slug'])

@BLUEPRINT.route("/<path:slug>/edit", methods=['GET'])
def edit(slug, redirectFrom=None, preview=None, collision=None):
    """Show the editing form for a page"""
    revision = model.Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
                               page=revision.page, title=revision.page.title,
                               revision=revision,
                               slug=revision.page.slug,
                               redirectFrom=redirectFrom,
                               collision=collision)
    else:
        page = None

        try:
            page = model.Page.get(slug=slug)
        except peewee.DoesNotExist:
            pass

        _, title = model.SlugField.split_title(slug)

        return render_template('404.html',
                               slug=slug,
                               title=title, page=page,
                               redirectFrom=redirectFrom)

@BLUEPRINT.route("/", methods=['POST'])
@BLUEPRINT.route("/<path:slug>/edit", methods=['POST'])
def save(slug=None):
    """Save a new Revision, creating a new Page if needed"""
    newslug = request.form['slug']
    title = request.form['title']
    if slug is None:
        slug = current_app.config['INDEX_PAGE']
    if slug != newslug:
        try:
            oldPage = model.Page.get(slug=newslug)
            logging.debug("Attempted rename of %s to %s", slug, newslug)
            return edit(slug, collision="Cannot change URL! Something already exists there.")
        except peewee.DoesNotExist:
            pass
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Updating existing page: %s", page.slug)
        page.title = title
        page.slug = newslug
        page.save()
    except peewee.DoesNotExist:
        print "Saving '%s' at '%s'" %(title, slug)
        page = model.Page.create(title=title,
                                 slug=slug)
        logging.debug("Created new page: %s (%s)", page.title, page.slug)
    page.newRevision(request.form['body'], request.form['message'],
                     request.form['author'])
    session = request.environ['beaker.session']
    session['author'] = request.form['author']
    session.save()

    return redirect(url_for('pages.view', slug=page.slug))

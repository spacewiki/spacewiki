"""Routes to handle the realtime editor"""

from flask import (Blueprint, current_app, render_template, request, redirect,
        url_for, flash)
from flask_login import current_user
from spacewiki import model, auth
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

        deletedPage = None
        try:
            deletedPage = model.Page.get(slug=slug, include_deleted=True)
        except peewee.DoesNotExist:
            pass

        return render_template('404.html',
                               slug=slug,
                               title=title, page=page, deletedPage=deletedPage,
                               redirectFrom=redirectFrom)

@BLUEPRINT.route("/", methods=['POST'])
@BLUEPRINT.route("/<path:slug>", methods=['POST'])
@auth.tripcodes.tripcode_login_field('author')
def save(slug=None):
    """Save a new Revision, creating a new Page if needed"""
    action = request.form.get('action', None)
    newslug = request.form.get('slug', None)
    title = request.form.get('title', None)
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
        page = model.Page.get(slug=slug, include_deleted=True)
        logging.debug("Updating existing page: %s", page.slug)
        page.title = title
        page.slug = newslug
        page.deleted = False
        page.save()
    except peewee.DoesNotExist:
        print "Saving '%s' at '%s'" %(title, slug)
        page = model.Page.create(title=title,
                                 slug=slug)
        logging.debug("Created new page: %s (%s)", page.title, page.slug)
    if action == "delete":
        page.markDeleted(current_user._get_current_object())
        flash("Page deleted!")
    else:
        page.newRevision(request.form['body'], request.form['message'],
                         current_user._get_current_object())

    return redirect(url_for('pages.view', slug=page.slug))

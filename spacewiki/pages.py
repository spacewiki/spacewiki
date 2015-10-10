"""Routes related to viewing and editing pages"""

from flask import (Blueprint, request, current_app, redirect, url_for,
                   render_template)
import logging
import peewee

from spacewiki import model

BLUEPRINT = Blueprint('pages', __name__)


@BLUEPRINT.route("/", methods=['POST'])
@BLUEPRINT.route("/<path:slug>", methods=['POST'])
def save(slug=None):
    """Save a new Revision, creating a new Page if needed"""
    if slug is None:
        slug = current_app.config['INDEX_PAGE']
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Updating existing page: %s", page.slug)
    except peewee.DoesNotExist:
        slug, title = model.SlugField.mangle_full_slug(slug, request.form['title'])
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


@BLUEPRINT.route("/preview", methods=['POST'])
def preview():
    """Render some markup as HTML"""
    return model.Revision.render_text(request.form['body'],
                                      request.form['slug'])


@BLUEPRINT.route("/<path:slug>/edit", methods=['GET'])
def edit(slug, redirectFrom=None, preview=None):
    """Show the editing form for a page"""
    revision = model.Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
                               page=revision.page, revision=revision,
                               slug=revision.page.slug,
                               redirectFrom=redirectFrom)
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


@BLUEPRINT.route("/", methods=['GET'])
@BLUEPRINT.route("/<path:slug>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>@<revision>", methods=['GET'])
def view(slug=None, revision=None, redirectFrom=None):
    if slug is None:
        slug = current_app.config['INDEX_PAGE']

    last_page = None

    if revision is None:
        revision = model.Page.latestRevision(slug)
    else:
        revision = model.Revision.get(id=revision)

    last_page_slug = \
        model.Page.parsePreviousSlugFromRequest(
            request,
            current_app.config['INDEX_PAGE']
        )

    if last_page_slug is not None:
        try:
            last_page = model.Page.get(slug=last_page_slug)
        except peewee.DoesNotExist:
            pass

    if revision is not None:
        if last_page is not None and last_page != revision.page:
            revision.page.makeSoftlinkFrom(last_page)

        if revision.body.startswith("#Redirect"):
            new_slug = revision.body.split(' ', 1)[1]
            logging.debug("Redirect to %s", new_slug)

            return view(slug=new_slug, redirectFrom=slug)

        return render_template('page.html',
                               revision=revision, page=revision.page,
                               redirectFrom=redirectFrom)
    else:
        return edit(slug, redirectFrom=redirectFrom)

"""Routes related to viewing and editing pages"""

from flask import (Blueprint, request, current_app, redirect, url_for,
                   render_template, make_response, send_from_directory)
import logging
import peewee

from spacewiki import model

BLUEPRINT = Blueprint('pages', __name__)


@BLUEPRINT.route("/", methods=['POST'])
@BLUEPRINT.route("/<path:slug>", methods=['POST'])
def save(slug=None):
    """Save a new Revision, creating a new Page if needed"""
    slug = request.form['slug']
    title = request.form['title']
    if slug is None:
        slug = current_app.config['INDEX_PAGE']
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Updating existing page: %s", page.slug)
        page.title = title
        page.slug = slug
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
                               page=revision.page, title=revision.page.title,
                               revision=revision,
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
@BLUEPRINT.route("/.<string:extension>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>.<string:extension>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>@<revision>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>@<revision>.<string:extension>", methods=['GET'])
def view(slug=None, revision=None, extension=None, redirectFrom=None):
    if slug is None:
        slug = current_app.config['INDEX_PAGE']

    if slug.startswith('static/'):
        static_path = slug[len('static/'):] + '.' + extension
        return current_app.send_static_file(static_path)

    last_page = None

    if revision is None:
        revision = model.Page.latestRevision(slug)
    else:
        revision = model.Revision.get(id=revision)
    
    if revision is not None and extension is not None:
        extension = extension.lower()
        if extension == "md":
            return make_response(revision.body, 200, {'Content-type': 'text/plain'})
        else:
            raise KeyError

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

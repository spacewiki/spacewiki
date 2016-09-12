"""Routes related to viewing and editing pages"""

from flask import (Blueprint, request, current_app, redirect, url_for,
                   render_template, make_response, send_from_directory)
import logging
import peewee

from spacewiki import model, editor

BLUEPRINT = Blueprint('pages', __name__)

@BLUEPRINT.route("/", methods=['GET'])
@BLUEPRINT.route("/.<string:extension>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>.<string:extension>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>@<revision>", methods=['GET'])
@BLUEPRINT.route("/<path:slug>@<revision>.<string:extension>", methods=['GET'])
def view(slug=None, revision=None, extension=None, redirectFrom=None,
        missingIndex=False):

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
        elif last_page is not None:
            logging.debug("Could not parse referrer: %s", last_page_slug)

        if revision.body.startswith("#Redirect"):
            new_slug = revision.body.split(' ', 1)[1]
            logging.debug("Redirect to %s", new_slug)

            return view(slug=new_slug, redirectFrom=slug)

        return render_template('page.html',
                               revision=revision, page=revision.page,
                               redirectFrom=redirectFrom,
                               missingIndex=missingIndex)
    else:
        if slug == current_app.config['INDEX_PAGE']:
            return view(slug='docs', redirectFrom=slug, missingIndex=True)
        else:
            return editor.edit(slug, redirectFrom=redirectFrom)

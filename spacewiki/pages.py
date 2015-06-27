from flask import Blueprint, request, current_app, redirect, url_for, render_template
import peewee

import model

bp = Blueprint('pages', __name__)

@bp.route("/<slug>", methods=['POST'])
def save(slug):
    """Save a new Revision, creating a new Page if needed"""
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Updating existing page: %s", page.slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=request.form['title'], slug=request.form['title'])
        logging.debug("Created new page: %s (%s)", page.title, page.slug)
    page.newRevision(request.form['body'], request.form['message'],
        request.form['author'])
    session = request.environ['beaker.session']
    session['author'] = request.form['author']
    session.save()
    return redirect(url_for('pages.view', slug=page.slug))

@bp.route("/preview", methods=['POST'])
def preview():
    """Render some markup as HTML"""
    return model.Revision.render_text(request.form['body'],
        request.form['slug'])

@bp.route("/<slug>/edit", methods=['GET'])
def edit(slug, redirectFrom=None, preview=None):
    """Show the editing form for a page"""
    revision = model.Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
            page=revision.page, revision=revision, slug=revision.page.slug,
            redirectFrom=redirectFrom)
    else:
        page = None
        try:
            page = model.Page.get(slug=slug)
        except peewee.DoesNotExist:
            pass
        return render_template('404.html',
            slug=model.SlugField.slugify(slug), title=slug, page=page, redirectFrom=redirectFrom)

@bp.route("/", methods=['GET'])
@bp.route("/<slug>", methods=['GET'])
@bp.route("/<slug>/<revision>", methods=['GET'])
def view(slug=None, revision=None, redirectFrom=None):
    if slug is None:
        slug = current_app.config['INDEX_PAGE']
    lastPage = None
    if revision is None:
      revision = model.Page.latestRevision(slug)
    else:
      revision = model.Revision.get(id=revision)

    lastPageSlug = model.Page.parsePreviousSlugFromRequest(request,
    current_app.config['INDEX_PAGE'])
    if lastPageSlug is not None:
        try:
            lastPage = model.Page.get(slug=lastPageSlug)
        except peewee.DoesNotExist:
            pass

    if revision is not None:
        if lastPage is not None and lastPage != revision.page:
            revision.page.makeSoftlinkFrom(lastPage)

        if revision.body.startswith("#Redirect"):
            newSlug = revision.body.split(' ', 1)[1]
            logging.debug("Redirect to %s", newSlug)
            return view(slug=newSlug, redirectFrom=slug)
        return render_template('page.html',
            revision=revision, page=revision.page, redirectFrom=redirectFrom)
    else:
        return edit(slug, redirectFrom=redirectFrom)

#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for
from flask.ext.misaka import Misaka
from argparse import ArgumentParser
import logging
import urlparse
import urllib
import settings

import model
import context
import filters

app = Flask(__name__)
Misaka(app)
context.init(app)
filters.init(app)


@app.before_request
def setup_db():
    """Connect to the database before a request is handled"""
    g.database = model.database
    g.database.connect()

@app.teardown_appcontext
def close_db(error): #pylint: disable=unused-argument
    """Close the database connection when the app is shutting down"""
    if hasattr(g, 'database'):
        try:
            g.database.close()
        except: #pylint: disable=bare-except
            pass
        del g.database


@app.route("/.history/<slug>")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)

@app.route('/.revision/<revID>')
def revision(revID):
    """View a specific revision of a page"""
    revision = model.Revision.get(id=revID)
    return render_template('revision.html', revision=revision)

@app.route("/<slug>", methods=['POST'])
def save(slug):
    """Save a new Revision, creating a new Page if needed"""
    slug = model.SlugField.slugify(slug)
    try:
        page = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=request.form['title'], slug=request.form['title'])
    page.newRevision(request.form['body'])
    return redirect(url_for('view', slug=page.slug))

@app.route("/.edit/<slug>", methods=['GET'])
def edit(slug, redirectFrom=None):
    """Show the editing form for a page"""
    revision = model.Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
            revision=revision, slug=revision.page.slug,
            redirectFrom=redirectFrom)
    else:
        return render_template('404.html',
            slug=model.SlugField.slugify(slug), title=slug, redirectFrom=redirectFrom)

@app.route("/.search")
def search():
    query = request.args.get('q')
    pages = model.Page.select().where(model.Page.title.contains(query))
    return render_template('search.html', results=pages, query=query)

@app.route("/.all-pages")
def allPages():
    pages = model.Page.select().order_by(model.Page.title)
    return render_template('all-pages.html',
        pages=pages)

@app.route("/")
@app.route("/<slug>")
@app.route("/<slug>/<revision>")
def view(slug=settings.INDEX_PAGE, revision=None, redirectFrom=None):
    lastPage = None
    if revision is None:
      revision = model.Page.latestRevision(slug)
    else:
      revision = model.Revision.get(id=revision)

    if 'Referer' in request.headers:
        referer = request.headers['Referer']
        referUrl = urlparse.urlparse(referer)
        if referUrl.netloc == request.headers['Host']:
            lastPageSlug = urllib.unquote(referUrl.path[1:])
            logging.debug("Last page slug: %s", lastPageSlug)
            if lastPageSlug != settings.INDEX_PAGE:
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
            return index(newSlug, redirectFrom=slug)
        return render_template('page.html',
            revision=revision, redirectFrom=redirectFrom)
    else:
        return edit(slug, redirectFrom=redirectFrom)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--syncdb', action='store_const',
        default=False, const=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.syncdb:
        logging.info("Creating tables...")
        try:
            model.Page.select().execute()
        except peewee.OperationalError:
            with app.app_context():
                model.database.create_tables([model.Page, model.Revision, model.Softlink])
        for page in model.Page.select():
            page.slug = model.SlugField.slugify(page.slug)
            page.save()
        logging.info("OK!")
    else:
        app.run(debug=True)

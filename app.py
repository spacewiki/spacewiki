#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for, Response
from werkzeug import secure_filename
from flask.ext.misaka import Misaka
from argparse import ArgumentParser
import logging
import os
import settings
import tempfile
import urlparse
import urllib

import model
import context
import filters

app = Flask(__name__)
app.config['UPLOAD_PATH'] = settings.UPLOAD_PATH
Misaka(app)
context.init(app)
filters.init(app)

if settings.ADMIN_EMAILS:
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
        'spacewiki@localhost',
        settings.ADMIN_EMAILS, 'SpaceWiki error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

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


@app.route("/<slug>/history")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)

@app.route("/<slug>/attach")
def upload(slug):
    """Show the file attachment form"""
    page = model.Page.get(slug=slug)
    return render_template('attach.html', page=page)

@app.route("/<slug>/attach", methods=['POST'])
def attach(slug):
    """Handle saving a file upload"""
    page = model.Page.get(slug=slug)
    file = request.files['file']
    fname = secure_filename(file.filename)
    tmpname = os.path.join(tempfile.mkdtemp(), "upload")
    with model.database.transaction():
        file.save(tmpname)
        page.attachUpload(tmpname, fname, app.config['UPLOAD_PATH'])
    return redirect(url_for('view', slug=page.slug))

@app.route("/<slug>/file/<fileslug>")
def get_attachment(slug, fileslug):
    """FIXME: This select/join should be handled by the models"""
    attachment = model.Attachment.select().join(model.Page).where(model.Attachment.slug == fileslug,
        model.Page.slug == slug)[0]
    latestRevision = attachment.revisions[0]
    def generate():
        f = open(os.path.join(app.config['UPLOAD_PATH'],
          latestRevision.sha+"-"+attachment.filename), 'r')
        buf = f.read(2048)
        while buf:
            yield buf
            buf = f.read(2048)
    """FIXME: mimetype detection"""
    mimetype = 'image/jpeg; charset=binary'
    return Response(generate(), mimetype=mimetype)

@app.route("/<slug>", methods=['POST'])
def save(slug):
    """Save a new Revision, creating a new Page if needed"""
    slug = model.SlugField.slugify(slug)
    try:
        page = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=request.form['title'], slug=request.form['title'])
    page.newRevision(request.form['body'], request.form['message'])
    return redirect(url_for('view', slug=page.slug))

@app.route("/<slug>/edit", methods=['GET'])
def edit(slug, redirectFrom=None):
    """Show the editing form for a page"""
    revision = model.Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
            page=revision.page, revision=revision, slug=revision.page.slug,
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
            script_name = '/'

            if 'SCRIPT_NAME' in os.environ:
                script_name = os.environ['SCRIPT_NAME']

            lastPageSlug = urllib.unquote(referUrl.path[len(script_name)+1:])
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
            return view(slug=newSlug, redirectFrom=slug)
        return render_template('page.html',
            revision=revision, page=revision.page, redirectFrom=redirectFrom)
    else:
        return edit(slug, redirectFrom=redirectFrom)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--syncdb', action='store_const',
        default=False, const=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.syncdb:
        model.syncdb(app)
    else:
        app.run(debug=True)

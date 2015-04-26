#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for, Response
from werkzeug import secure_filename
import werkzeug.exceptions
import werkzeug
from argparse import ArgumentParser
import logging
import os
import settings
import tempfile
from PIL import Image

import model
import context

app = Flask(__name__)
app.config.from_object('settings')

model.setURI(app.config['DATABASE'])
context.init(app)

if settings.ADMIN_EMAILS:
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
        'spacewiki@localhost',
        settings.ADMIN_EMAILS, 'SpaceWiki error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

@app.route("/<slug>/revert/<revision>")
def revert(slug, revision):
    page = model.Page.get(slug=slug)
    oldRevision = model.Revision.get(page=page, id=revision)
    page.newRevision(oldRevision.body, "Revert to revision %s from %s"%(oldRevision.id, oldRevision.timestamp))
    return redirect(url_for('view', slug=page.slug))

@app.route("/<slug>/history")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)

@app.route("/<slug>/attach")
def upload(slug):
    """Show the file attachment form"""
    try:
        page = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=slug, slug=slug)
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
@app.route("/<slug>/file/<fileslug>/<size>")
def get_attachment(slug, fileslug, size=None):
    """FIXME: This select/join should be handled by the models"""
    attachment = model.Attachment.select().join(model.Page).where(model.Attachment.slug == fileslug,
        model.Page.slug == slug)[0]
    latestRevision = attachment.revisions[0]
    maxSize = None

    if size is not None:
        try:
            maxSize = max(0, int(size))
        except ValueError, e:
            maxSize = -1

    if maxSize is not None and maxSize <= 0:
        raise werkzeug.exceptions.NotFound()

    def generate():
        fname = model.Attachment.hashPath(latestRevision.sha,
            attachment.filename)
        if maxSize is not None:
            resizedFname = os.path.join(app.config['UPLOAD_PATH'], fname)+'-%s'%(maxSize)
            if not os.path.exists(resizedFname):
                img = Image.open(os.path.join(app.config['UPLOAD_PATH'], fname))
                w, h = img.size
                if w > h:
                  scale = float(maxSize) / w
                  w = maxSize
                  h = h * scale
                else:
                  scale = float(maxSize) / h
                  h = maxSize
                  w = w * scale
                img.thumbnail([w, h], Image.ANTIALIAS)
                img.save(resizedFname, format='png')
            f = open(resizedFname, 'r')
        else:
            f = open(os.path.join(app.config['UPLOAD_PATH'], fname))
        buf = f.read(2048)
        while buf:
            yield buf
            buf = f.read(2048)
    """FIXME: mimetype detection"""
    mimetype = 'image/png; charset=binary'
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
        page = None
        try:
            page = model.Page.get(slug=slug)
        except peewee.DoesNotExist:
            pass
        return render_template('404.html',
            slug=model.SlugField.slugify(slug), title=slug, page=page, redirectFrom=redirectFrom)

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

    lastPageSlug = model.Page.parsePreviousSlugFromRequest(request,
    app.config['INDEX_PAGE'])
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

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--syncdb', action='store_const',
        default=False, const=True)
    args = parser.parse_args()

    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    if args.syncdb:
        model.syncdb()
    else:
        app.run(debug=True)

#!/usr/bin/env python
from argparse import ArgumentParser
from beaker.middleware import SessionMiddleware
from flask import Flask, g, render_template, request, redirect, url_for, Response, current_app
import logging
import peewee
import tempfile
import werkzeug
import werkzeug.exceptions

import model
import context
import uploads

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object('spacewiki.settings')
app.register_blueprint(context.bp)
app.register_blueprint(model.bp)
app.register_blueprint(uploads.bp)

if app.config['TEMP_DIR'] is None:
    app.config['TEMP_DIR'] = tempfile.mkdtemp(prefix='spacewiki')

app.wsgi_app = SessionMiddleware(app.wsgi_app, {
  'session.type': 'file',
  'session.cookie_expires': False,
  'session.data_dir': app.config['TEMP_DIR']
})

if app.config['ADMIN_EMAILS']:
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
        'spacewiki@localhost',
        app.config['ADMIN_EMAILS'], 'SpaceWiki error')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

@app.route("/<slug>/revert", methods=['POST'])
def revert(slug):
    revision = request.form['revision']
    message = request.form['message']
    author = request.form['author']
    page = model.Page.get(slug=slug)
    oldRevision = model.Revision.get(page=page, id=revision)
    page.newRevision(oldRevision.body, "Revert to revision %s from %s: %s"
        %(oldRevision.id, oldRevision.timestamp, message), author)
    session = request.environ['beaker.session']
    session['author'] = author
    session.save()
    return redirect(url_for('view', slug=page.slug))

@app.route("/<slug>/history")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)

@app.route("/<slug>", methods=['POST'])
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
    return redirect(url_for('view', slug=page.slug))

@app.route("/preview", methods=['POST'])
def preview():
    """Render some markup as HTML"""
    return model.Revision.render_text(request.form['body'],
        request.form['slug'])

@app.route("/<slug>/edit", methods=['GET'])
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

@app.route("/", methods=['GET'])
@app.route("/<slug>", methods=['GET'])
@app.route("/<slug>/<revision>", methods=['GET'])
def view(slug=app.config['INDEX_PAGE'], revision=None, redirectFrom=None):
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

@app.route('/<slug>/<start>..<end>')
def diff(slug, start, end):
    fromRev = model.Revision.get(id=start)
    toRev = model.Revision.get(id=end)
    return render_template('diff.html',
        fromRev=fromRev, toRev=toRev,
        diff=fromRev.diffTo(toRev), page=fromRev.page)

#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for
from flask.ext.misaka import Misaka
from argparse import ArgumentParser
import logging
import re
import urlparse
import urllib

import settings

app = Flask(__name__)
Misaka(app)

database = peewee.SqliteDatabase(settings.DATABASE, threadlocals=True)

@app.context_processor
def add_site_settings():
    return dict(settings=settings)

linkSyntax = re.compile("\[\[(.+?)\]\]")
titledLinkSyntax = re.compile("\[\[(.+?)\|(.+?)\]\]")
def make_wikilink(match):
    groups = match.groups()
    if len(groups) == 1:
        title = groups[0]
        link = groups[0]
    else:
        title = groups[1]
        link = groups[0]
    return "[%s](%s)"%(title, link)

@app.template_filter('wikilinks')
def wikilinks(s):
    s = titledLinkSyntax.sub(make_wikilink, s)
    s = linkSyntax.sub(make_wikilink, s)
    return s

@app.before_request
def setup_db():
    g._database = database
    g._database.connect()

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, '_database'):
        g._database.close()

class BaseModel(peewee.Model):
    class Meta:
        database = database

class Page(BaseModel):
    title = peewee.CharField(unique=True)
    slug = peewee.CharField(unique=True)

    def newRevision(self, body):
        return Revision.create(page=self, body=body)

    def makeSoftlinkFrom(self, prev):
        logging.debug("Linking from %s to %s", prev.slug, self.slug)
        try:
            Softlink.get(Softlink.src == prev, Softlink.dest == self)
            logging.debug("Link exists!")
        except peewee.DoesNotExist:
            Softlink.create(src=prev, dest=self)
            logging.debug("New link!")
        Softlink.update(hits = Softlink.hits + 1).where(Softlink.src ==
            prev, Softlink.dest == self).execute()

    @classmethod
    def latestRevision(cls, slug):
        try:
            return Revision.select() \
                .join(cls) \
                .where(cls.slug == slug) \
                .order_by(Revision.id.desc())[0]
        except IndexError:
            return None

class Softlink(BaseModel):
    src = peewee.ForeignKeyField(Page, related_name='softlinks_out')
    dest = peewee.ForeignKeyField(Page, related_name='softlinks_in')
    hits = peewee.IntegerField(default=0)

class Revision(BaseModel):
    page = peewee.ForeignKeyField(Page, related_name='revisions')
    body = peewee.TextField()

@app.route("/.save", methods=['POST'])
def save():
    try:
      page = Page.get(slug=request.form['title'])
    except peewee.DoesNotExist:
      page = Page.create(slug=request.form['title'],
          title=request.form['title'])
    rev = page.newRevision(request.form['body'])
    return redirect(url_for('index', slug=request.form['title']))

@app.route("/.edit/<slug>", methods=['GET'])
def edit(slug):
    revision = Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
            revision=revision)
    else:
        return render_template('404.html',
            slug=slug)

@app.route("/.all-pages")
def allPages():
    pages = Page.select().order_by(Page.title)
    return render_template('all-pages.html',
        pages=pages)

@app.route("/")
@app.route("/<slug>")
def index(slug=settings.INDEX_PAGE, redirectFrom=None):
    lastPage = None
    revision = Page.latestRevision(slug)

    if 'Referer' in request.headers:
        referer = request.headers['Referer']
        referUrl = urlparse.urlparse(referer)
        if referUrl.netloc == request.headers['Host']:
            lastPageSlug = urllib.unquote(referUrl.path[1:])
            logging.debug("Last page slug: %s", lastPageSlug)
            if lastPageSlug != settings.INDEX_PAGE:
                try:
                    lastPage = Page.get(slug=lastPageSlug)
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
        return render_template('404.html',
            slug=slug, redirectFrom=redirectFrom)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--syncdb', action='store_const',
        default=False, const=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG)

    if args.syncdb:
      logging.info("Creating tables...")
      with app.app_context():
        database.create_tables([Page, Revision, Softlink])
      logging.info("OK!")
    else:
      app.run()

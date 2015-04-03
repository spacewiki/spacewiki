#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for
from flask.ext.misaka import Misaka
from argparse import ArgumentParser
import logging
import re

DATABASE = 'spacewiki.sqlite3'

app = Flask(__name__)
Misaka(app)

database = peewee.SqliteDatabase(DATABASE, threadlocals=True)

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

    @classmethod
    def latestRevision(cls, slug):
        try:
            return Revision.select() \
                .join(cls) \
                .where(cls.slug == slug) \
                .order_by(Revision.id.desc())[0]
        except IndexError:
            return None

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
def index(slug='Index', redirectFrom=None):
    revision = Page.latestRevision(slug)
    if revision is not None:
        if revision.body.startswith("#Redirect"):
            newSlug = revision.body.split(' ', 1)[1]
            print "Redirect to", newSlug
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
        database.create_tables([Page, Revision])
      logging.info("OK!")
    else:
      app.run()

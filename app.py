#!/usr/bin/env python
import peewee
from flask import Flask, g, render_template, request, redirect, url_for
from flask.ext.misaka import Misaka
from argparse import ArgumentParser
import logging
import re
import urlparse
import urllib
import bleach
import git
import os

import settings

app = Flask(__name__)
Misaka(app)

database = peewee.SqliteDatabase(settings.DATABASE, threadlocals=True)

@app.context_processor
def add_git_version():
    repo = git.Repo(os.path.dirname(os.path.realpath(__file__)))
    return dict(git_version=repo.head.commit.hexsha)

@app.context_processor
def add_random_page():
    page = None
    try:
        page = Page.select().order_by(peewee.fn.Random()).limit(1)[0]
    except:
        pass
    return dict(random_page=page)

@app.context_processor
def add_site_settings():
    return dict(settings=settings)

tag_whitelist = [
  'ul', 'li', 'ol', 'p', 'table', 'div', 'tr', 'th', 'td', 'em', 'big', 'b',
  'strong', 'a', 'abbr', 'aside', 'audio', 'blockquote', 'br', 'button', 'code',
  'dd', 'del', 'dfn', 'dl', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i',
  'img', 'ins', 'kbd', 'pre', 's', 'small', 'span', 'sub', 'sup', 'u', 'video'
]
@app.template_filter('safetags')
def safetags(s):
    return bleach.clean(s, tags=tag_whitelist, strip_comments=False)

templateSyntax = re.compile("\{\{(.+?)\}\}")
def do_template(match, depth):
    slug = match.groups()[0]
    if depth > 10:
      return "{{Max include depth of %s reached before [[%s]]}}"%(depth, slug)
    replacement = Page.latestRevision(slug)
    if replacement is None:
        return "{{[[%s]]}}"%(slug)
    return wikitemplates(replacement.body, depth=depth+1)

@app.template_filter('wikitemplates')
def wikitemplates(s, depth=0):
    def r(*args):
      return do_template(*args, depth=depth)
    return templateSyntax.sub(r, s)

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
        try:
            g._database.close()
        except:
            pass
        del g._database

class BaseModel(peewee.Model):
    class Meta:
        database = database

class SlugField(peewee.CharField):
    def coerce(self, value):
        return self.slugify(value)

    @staticmethod
    def slugify(title):
        return re.sub('[^\w]', '_', title.lower())

class Page(BaseModel):
    title = peewee.CharField(unique=True)
    slug = SlugField(unique=True)

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

@app.route("/.history/<slug>")
def history(slug):
    page = Page.get(slug=slug)
    return render_template('history.html', page=page)

@app.route('/.revision/<revision>')
def revision(revision):
    revision = Revision.get(id=revision)
    return render_template('revision.html', revision=revision)

@app.route("/.save/<slug>", methods=['POST'])
def save(slug):
    try:
      page = Page.get(slug=slug)
    except peewee.DoesNotExist:
      page = Page.create(title=request.form['title'], slug=request.form['title'])
    rev = page.newRevision(request.form['body'])
    return redirect(url_for('index', slug=page.slug))

@app.route("/.edit/<slug>", methods=['GET'])
def edit(slug, redirectFrom=None):
    revision = Page.latestRevision(slug)
    if revision is not None:
        return render_template('edit.html',
            revision=revision, slug=revision.page.slug,
            redirectFrom=redirectFrom)
    else:
        return render_template('404.html',
            slug=SlugField.slugify(slug), title=slug, redirectFrom=redirectFrom)

@app.route("/.search")
def search():
    query = request.args.get('q')
    pages = Page.select().where(Page.title.contains(query))
    return render_template('search.html', results=pages, query=query)

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
        Page.select().execute()
      except peewee.OperationalError:
        with app.app_context():
          database.create_tables([Page, Revision, Softlink])
      for page in Page.select():
        page.slug = SlugField.slugify(page.slug)
        page.save()
      logging.info("OK!")
    else:
      app.run(debug=True)

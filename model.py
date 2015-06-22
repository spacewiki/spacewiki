"""spacewiki database models"""
import bs4
import re
import difflib
import datetime
import logging
import hashlib
import mistune
import peewee
import playhouse.migrate
from playhouse.db_url import connect
import shutil
import urlparse
import urllib
import os
import slugify
import crypt
from werkzeug.local import LocalProxy
from flask import g, current_app
from flask.ext.script import Manager

import wikiformat

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        logging.debug("New db at %s!"%(current_app.config['DATABASE']))
        g._database = db = connect(current_app.config['DATABASE'])
    return db

database = LocalProxy(get_db)

class BaseModel(peewee.Model):
    class Meta:
        database = database

class SlugField(peewee.CharField):
    def coerce(self, value):
        return self.slugify(value)

    @staticmethod
    def slugify(title):
        """Translates a string into a reduced character set"""
        return slugify.slugify(unicode(title))

class TripcodeField(peewee.CharField):
    def coerce(self, value):
        return self.tripcode(value)

    @staticmethod
    def tripcode(value):
        tokens = value.split('#', 1)
        if len(tokens) == 1:
            return tokens[0]
        return tokens[0]+'#'+crypt.crypt(tokens[0], tokens[1])

class Page(BaseModel):
    title = peewee.CharField(unique=True)
    slug = SlugField(unique=True)

    @staticmethod
    def parsePreviousSlugFromRequest(req, default):
        if 'Referer' in req.headers:
            referer = req.headers['Referer']
            referUrl = urlparse.urlparse(referer)
            if 'Host' in req.headers:
                if referUrl.netloc == req.headers['Host']:
                    script_name = req.environ['SCRIPT_NAME']

                    lastPageSlug = urllib.unquote(referUrl.path[len(script_name)+1:])
                    if '/' in lastPageSlug:
                      lastPageSlug, _ = lastPageSlug.split('/', 1)
                    if lastPageSlug == "":
                        lastPageSlug = default
                    req.lastSlug = lastPageSlug
                    return lastPageSlug
        if 'lastSlug' in req.args:
            req.lastSlug = req.args.get('lastSlug')
            return req.lastSlug
        req.lastSlug = None
        return None

    def newRevision(self, body, message, author):
        """Creates a new Revision of this Page with the given body"""
        logging.debug("Creating new revision on %s", self.slug)
        return Revision.create(page=self, body=body, message=message,
            author=author)

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

    def attachUpload(self, src, filename, uploadPath):
        assert(isinstance(src, basestring))
        assert(isinstance(filename, basestring))
        assert(isinstance(uploadPath, basestring))

        logging.info("Attaching upload %s (%s), saved at %s", src, filename, uploadPath)

        hexSha = Attachment.hashFile(src)
        savedName = os.path.join(uploadPath, Attachment.hashPath(hexSha, filename))
        if not os.path.exists(os.path.dirname(savedName)):
            os.makedirs(os.path.dirname(savedName))
        shutil.move(src, savedName)
        """FIXME: These db queries should be handled by the model"""
        try:
            attachment = Attachment.get(page=self, slug=filename)
            logging.debug("Updating existing attachment: %s", attachment.slug)
        except peewee.DoesNotExist:
            attachment = Attachment.create(page=self, filename=filename,
                slug=filename)
            logging.debug("Creating new attachment: %s", attachment.slug)
        try:
            AttachmentRevision.get(attachment=attachment, sha=hexSha)
            logging.debug("Duplicate file upload: %s", attachment.slug)
        except peewee.DoesNotExist:
            AttachmentRevision.create(attachment=attachment, sha=hexSha)
            logging.debug("New upload: %s -> %s", attachment.slug, hexSha)
        logging.info("Uploaded file %s to %s"%(filename, savedName))

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

class WikiRenderer(mistune.Renderer):
    def block_html(self, html):
        firstLine, rest = html.split('\n', 1)
        tag, tagTail = re.match('^<(.+?)>(.*)', html).groups()
        rest = tagTail + rest
        renderer = WikiRenderer()
        md = mistune.Markdown(renderer=renderer)
        submd = md.render(unicode(rest))
        ret = "<%s>%s"%(tag, submd)
        return ret

class Revision(BaseModel):
    page = peewee.ForeignKeyField(Page, related_name='revisions')
    body = peewee.TextField()
    message = peewee.TextField(default='')
    timestamp = peewee.DateTimeField(default=datetime.datetime.now)
    author = TripcodeField(default='Anonymous')

    @staticmethod
    def markdown(s):
        renderer = WikiRenderer()
        md = mistune.Markdown(renderer=renderer)
        return md.render(s)

    @property
    def html(self):
        return  \
            wikiformat.safetags(\
            self.markdown(\
            wikiformat.wikilinks(\
            wikiformat.wikitemplates(self.body, self.page.slug))))

    @property
    def is_latest(self):
      return Page.latestRevision(self.page.slug) == self

    @property
    def prev(self):
      try:
        return Revision.select().where(Revision.page == self.page, Revision.id <
            self.id).order_by(Revision.id.desc()).limit(1)[0]
      except IndexError:
        return None

    @classmethod
    def _makeDiff(cls, r1, r2):
        if r1 is None:
            d = difflib.unified_diff(
                "",
                r2.body.split("\n"),
                lineterm="",
                fromfile="%s@%s"%(r2.page.slug, 0),
                tofile="%s@%s"%(r2.page.slug, r2.id))
        elif r2 is None:
            d = difflib.unified_diff(
                r1.body.split("\n"),
                "",
                lineterm="",
                fromfile="%s@%s"%(r1.page.slug, r1.id),
                tofile="%s@%s"%(r1.page.slug, 0))
        else:
            d = difflib.unified_diff(
                r1.body.split("\n"),
                r2.body.split("\n"),
                lineterm="",
                fromfile="%s@%s"%(r1.page.slug, r1.id),
                tofile="%s@%s"%(r2.page.slug, r2.id))
        return cls._parseDiff(d)

    @staticmethod
    def _parseDiff(diff):
        ret = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                lineType = 'meta'
            elif line.startswith('@@'):
                lineType = 'context'
            elif line.startswith('+'):
                lineType = 'addition'
            elif line.startswith('-'):
                lineType = 'subtraction'
            ret.append({'contents': line, 'type': lineType})
        return ret

    def diffTo(self, prev):
        return self._makeDiff(self, prev)

    @property
    def diffToPrev(self):
        prev = self.prev
        if prev is not None:
            return self.diffTo(prev)
        return self._makeDiff(None, self)

    @property
    def diffToNext(self):
        next = self.next
        if next is not None:
          return self.diffTo(next)
        return self._makeDiff(self, None)

    def diffStatsToPrev(self):
        meta = {'additions': 0, 'subtractions': 0}
        for line in self.diffToPrev:
            if line['type'] == 'addition':
                meta['additions'] += 1
            if line['type'] == 'subtraction':
                meta['subtractions'] += 1
        return meta

    @property
    def next(self):
      try:
        return Revision.select().where(Revision.page == self.page, Revision.id >
            self.id).order_by(Revision.id).limit(1)[0]
      except IndexError:
        return None

class Attachment(BaseModel):
    page = peewee.ForeignKeyField(Page, related_name='attachments')
    filename = peewee.CharField(unique=True)
    slug = SlugField(unique=True)

    @staticmethod
    def hashFile(src):
        with open(src, 'r') as f:
            sha = hashlib.sha256()
            sha.update(f.read())
        return sha.hexdigest()

    @staticmethod
    def hashPath(sha, src):
        return "%s/%s/%s-%s"%(sha[0:2], sha[2:4], sha, src)

    @classmethod
    def findAttachment(cls, pageSlug, fileSlug):
        try:
            page = Page.get(slug=pageSlug)
        except peewee.DoesNotExist:
            return None
        try:
            attachment = Attachment.get(slug=fileSlug)
        except peewee.DoesNotExist:
            return None
        return attachment

    class Meta:
        indexes = (
            (('page', 'slug'), True),
        )

class AttachmentRevision(BaseModel):
    attachment = peewee.ForeignKeyField(Attachment, related_name='revisions')
    sha = peewee.CharField()

    class Meta:
        indexes = (
            (('attachment', 'sha'), True),
        )

class DatabaseVersion(BaseModel):
    schema_version = peewee.IntegerField(default=0)

MANAGER = Manager(usage='Database tools')

@MANAGER.command
def syncdb():
    """Creates and updates database schema"""
    logging.info("Creating tables...")
    try:
        DatabaseVersion.select().execute()
    except peewee.OperationalError:
        logging.debug("Creating initial database version table")
        database.create_tables([DatabaseVersion])
    try:
        v = DatabaseVersion.select()[0]
        logging.debug("Current database is at version %s", v.schema_version)
    except IndexError:
        logging.debug("Creating initial schema version of 0")
        v = DatabaseVersion.create(schema_version=0)
    v.schema_version = run_migrations(v.schema_version)
    v.save()
    logging.info("OK!")

MIGRATIONS = (
    lambda m: (
        m.add_column('revision', 'author', Revision.author),
    ),
)

def run_migrations(currentRevision):
    migrator = playhouse.migrate.SqliteMigrator(database)

    for model in (Page, Revision, Softlink, Attachment, AttachmentRevision):
        with database.transaction():
            try:
                model.get(id=0)
            except peewee.OperationalError:
                logging.debug("Creating table for %s", model.__name__)
                database.create_tables([model])
            except model.DoesNotExist:
                pass

    if currentRevision == 0:
      return len(MIGRATIONS)

    for migration in MIGRATIONS[currentRevision:]:
        with database.transaction():
            logging.debug("Applying migration %d", currentRevision)
            playhouse.migrate.migrate(*migration(migrator))
            currentRevision += 1

    return currentRevision

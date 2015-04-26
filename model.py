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
import settings
import shutil
import urlparse
import urllib
import os

import wikiformat

database = peewee.Proxy()
currentURI = None

def setURI(u):
    database.initialize(connect(u))
    database.connect()

class BaseModel(peewee.Model):
    class Meta:
        database = database

class SlugField(peewee.CharField):
    def coerce(self, value):
        return self.slugify(value)

    @staticmethod
    def slugify(title):
        """Translates a string into a reduced character set"""
        return re.sub(r'[^\w]', '_', title.lower())

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

    def newRevision(self, body, message):
        """Creates a new Revision of this Page with the given body"""
        return Revision.create(page=self, body=body, message=message)

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

        hexSha = Attachment.hashFile(src)
        savedName = os.path.join(uploadPath, Attachment.hashPath(hexSha, filename))
        if not os.path.exists(os.path.dirname(savedName)):
            os.makedirs(os.path.dirname(savedName))
        shutil.move(src, savedName)
        """FIXME: These db queries should be handled by the model"""
        try:
            attachment = Attachment.get(page=self, slug=filename)
        except peewee.DoesNotExist:
            attachment = Attachment.create(page=self, filename=filename,
                slug=filename)
        try:
            AttachmentRevision.create(attachment=attachment, sha=hexSha)
        except peewee.IntegrityError:
            print "Duplicate upload!"
        print "Uploaded file %s to %s"%(filename, savedName)

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

    @property
    def diffToPrev(self):
        prev = self.prev
        if prev is not None:
            ret = []
            for line in difflib.unified_diff(prev.body.split("\n"),
                self.body.split("\n"), lineterm="",
                fromfile="%s@%s"%(self.page.slug,self.id),
                tofile="%s@%s"%(self.page.slug,prev.id)):
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
        return difflib.unified_diff('', self.body)

    @property
    def diffToNext(self):
        next = self.next
        if next is not None:
            return difflib.unified_diff(self.body, next.body)
        return difflib.unified_diff(self.body, "")

    def diffStatsToPrev(self):
        meta = {'additions': 0, 'subtractions': 0}
        for line in self.diffToPrev:
            if line.startswith('+') and not line.startswith('+++'):
                meta['additions'] += 1
            if line.startswith('-') and not line.startswith('---'):
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

def syncdb():
    logging.info("Creating tables...")
    try:
        DatabaseVersion.select().execute()
    except peewee.OperationalError:
        database.create_tables([DatabaseVersion])
    try:
        v = DatabaseVersion.select()[0]
    except IndexError:
        v = DatabaseVersion.create(schema_version=0)
    v.schema_version = migrate(v.schema_version)
    v.save()
    logging.info("OK!")

def migrate(currentRevision):
    migrator = playhouse.migrate.SqliteMigrator(database)
    with database.transaction():
        if currentRevision == 0:
            database.create_tables([Page, Revision, Softlink, Attachment,
              AttachmentRevision])
            return migrate(1)
    return currentRevision

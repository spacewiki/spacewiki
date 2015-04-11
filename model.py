"""spacewiki database models"""
import bs4
import re
import datetime
import logging
import hashlib
import mistune
import peewee
import playhouse.migrate
import settings
import shutil
import os

import parser

database = peewee.SqliteDatabase(settings.DATABASE, threadlocals=True)

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
        soup = bs4.BeautifulSoup(html)
        container = soup.body.contents[0]
        result = ""
        for c in container.children:
            renderer = WikiRenderer()
            md = mistune.Markdown(renderer=renderer)
            subsoup = bs4.BeautifulSoup(md.render(str(c)))
            c.replace_with(subsoup.body.contents[0])
        return str(container)

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
            parser.safetags(\
            self.markdown(\
            parser.wikilinks(\
            parser.wikitemplates(self.body, self.page.slug))))

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

def syncdb(app):
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
            return migrate(3)
        if currentRevision == 1:
            playhouse.migrate.migrate(
                migrator.add_column('revision', 'message', Revision.message),
                migrator.add_column('revision', 'timestamp', Revision.timestamp)
            )
            return migrate(2)
        if currentRevision == 2:
            database.create_tables([Attachment, AttachmentRevision])
            return migrate(3)
    return currentRevision

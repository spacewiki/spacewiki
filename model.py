import peewee
import settings
import re

database = peewee.SqliteDatabase(settings.DATABASE, threadlocals=True)

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


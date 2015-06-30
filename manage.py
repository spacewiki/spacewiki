#!/usr/bin/env python
from flask.ext.script import Manager, Shell, Server
from spacewiki import model
import logging
import sys
import os
import os.path

sys.path.append(os.path.dirname(__file__))

from spacewiki.app import APP

MANAGER = Manager(APP)
MANAGER.add_command('db', model.MANAGER)
MANAGER.add_command('runserver', Server())
MANAGER.add_command("shell", Shell())

@MANAGER.command
def import_docs():
    from spacewiki import model
    model.get_db()
    doc_path = os.path.sep.join((os.path.dirname(__file__), 'doc'))
    for root, dirs, files in os.walk(doc_path):
        for fname in files:
            if fname.endswith(".md"):
                title = 'docs/' + '.'.join(fname.split(".")[0:-1])
            else:
                continue
            logging.info("Importing %s", fname)
            try:
                p = model.Page.get(slug=title)
            except model.Page.DoesNotExist:
                p = model.Page.create(title=title, slug=title)
            p.newRevision(open(fname, 'r').read(), 'Imported from %s' % fname, 'SpaceWiki')

if __name__ == "__main__":
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.basicConfig(level=logging.DEBUG)

    MANAGER.run()

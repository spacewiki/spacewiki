#!/usr/bin/env python
from flask.ext.script import Manager, Shell, Server
from spacewiki import model
import logging
import sys
import os
import os.path
import colorlog

sys.path.append(os.path.dirname(__file__))

from spacewiki.app import APP

MANAGER = Manager(APP)
MANAGER.add_command('db', model.MANAGER)
MANAGER.add_command("shell", Shell())

@MANAGER.option('-s', '--syncdb', dest='syncdb', help='Run syncdb on boot',
        default=False, action='store_true')
def runserver(syncdb):
    if (syncdb):
        model.syncdb()
    from spacewiki.app import APP
    from gevent.wsgi import WSGIServer
    serv = WSGIServer(('', 5000), APP, log=logging.getLogger("http"))
    serv.serve_forever()

@MANAGER.command
def import_docs():
    from spacewiki import model
    model.get_db()
    doc_path = os.path.sep.join((os.path.dirname(__file__), 'doc'))
    for root, dirs, files in os.walk(doc_path):
        for fname in files:
            if fname.endswith(".md"):
                title = '.'.join(fname.split(".")[0:-1])
                slug = 'docs/' + title
            else:
                continue
            logging.info("Importing %s", fname)
            if title == 'README':
                title = 'SpaceWiki Documentation'
                slug = 'docs'
            try:
                p = model.Page.get(slug=slug)
            except model.Page.DoesNotExist:
                p = model.Page.create(title=title, slug=slug)
            p.newRevision(open(os.path.sep.join((root, fname)), 'r').read(), 'Imported from %s' % fname, 'SpaceWiki')

if __name__ == "__main__":
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    logging.root.addHandler(handler)
    APP.logger.setLevel(logging.DEBUG)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)
    logging.getLogger('http').setLevel(logging.WARNING)
    logging.getLogger('peewee').setLevel(logging.INFO)
    logging.root.setLevel(logging.DEBUG)

    MANAGER.run()

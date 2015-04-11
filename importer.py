import requests
import re
import model
import logging
import peewee

def xlate_external_link(s):
    return "[%s](%s)"%(s.groups()[1], s.groups()[0])

def import_page(url, slug):
    wikitext = requests.get(url+'?title=%s&action=raw'%(slug)).text
    mdtext = re.sub('\[(\w+://.*?) (.+?)\]', xlate_external_link,
        wikitext, flags=re.MULTILINE | re.DOTALL)
    try:
        p = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        p = model.Page.create(title=slug, slug=slug)
    p.newRevision(mdtext, 'Import from %s'%(url))
    print mdtext

    links = re.findall('\[\[(.*)\]\]', mdtext)
    if links:
        for l in links:
            import_page(url, l)
    logging.info('Page "%s" imported.', slug)

"""Various context processors"""
from flask import Blueprint, request
import git
import os
import peewee

from spacewiki import model, settings

BLUEPRINT = Blueprint('context', __name__)


@BLUEPRINT.app_context_processor
def add_git_version():
    """Adds the current git sha to the template context"""
    try:
        repo = git.Repo(
            os.path.sep.join((
                os.path.dirname(os.path.realpath(__file__)),
                '..'
            ))
        )
        return dict(git_version=repo.head.commit.hexsha)
    except:
        return {'git_version': None}


@BLUEPRINT.app_context_processor
def add_random_page():
    """Adds a random page to the template context"""
    page = None
    try:
        page = model.Page.select().order_by(peewee.fn.Random()).limit(1)[0]
    except IndexError:
        pass
    return dict(random_page=page)


@BLUEPRINT.app_context_processor
def add_site_settings():
    """Adds the contents of settings.py to the template context"""
    return dict(settings=settings)


@BLUEPRINT.app_context_processor
def add_default_author():
    """Adds the default author to the template context"""
    session = request.environ['beaker.session']
    if 'author' in session:
        author = session['author']
    else:
        author = 'Anonymous'
    return dict(DEFAULT_AUTHOR=author)

@BLUEPRINT.app_context_processor
def add_nav_pages():
    pages = []
    nav_page = model.Page.latestRevision('.spacewiki/navigation-list')
    if nav_page:
        for link in nav_page.body.split('\n'):
            pageRev = model.Page.latestRevision(link)
            if pageRev:
                pages.append(pageRev.page)
    return dict(NAVIGATION_PAGES=pages)

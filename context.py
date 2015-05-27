"""Various context processors"""
import git
import model
import os
import peewee
import settings
from flask import Blueprint

bp = Blueprint('context', __name__)

@bp.app_context_processor
def add_git_version():
    """Adds the current git sha to the template context"""
    repo = git.Repo(os.path.dirname(os.path.realpath(__file__)))
    return dict(git_version=repo.head.commit.hexsha)

@bp.app_context_processor
def add_random_page():
    """Adds a random page to the template context"""
    page = None
    try:
        page = model.Page.select().order_by(peewee.fn.Random()).limit(1)[0]
    except IndexError:
        pass
    return dict(random_page=page)

@bp.app_context_processor
def add_site_settings():
    """Adds the contents of settings.py to the template context"""
    return dict(settings=settings)

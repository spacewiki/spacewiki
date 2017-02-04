"""Various context processors"""
from flask import Blueprint, request, current_app
import git
import os
import peewee

from spacewiki import model

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
def add_site_settings():
    """Adds the contents of settings.py to the template context"""
    return dict(settings=current_app.config)

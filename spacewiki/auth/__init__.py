from flask import Blueprint,  url_for, redirect, flash
from flask_login import LoginManager, login_required, \
        logout_user
from spacewiki import model
from spacewiki.auth import tripcodes
import logging

LOGIN_MANAGER = LoginManager()
@LOGIN_MANAGER.user_loader
def load_user(user_id):
    logging.debug("Loading logged in user %s", user_id)
    return model.Identity.get_from_id(user_id)

LOGIN_MANAGER.anonymous_user = tripcodes.new_anon_user

BLUEPRINT = Blueprint('auth', __name__)

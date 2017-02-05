from flask import request
from flask_login import login_user, current_user
from functools import wraps
import hashlib
import logging
from spacewiki import model

import random
import string

def tripcode_login_field(fieldname='author'):
    def decorator(f):
        @wraps(f)
        def d(*args, **kwargs):
            author_ident = request.form.get(fieldname, None)
            if author_ident is not None:
                tripcode_login(author_ident)
            return f(*args, **kwargs)
        return d
    return decorator

def tripcode_login(tripcode):
    hashed_tripcode = hash_tripcode(tripcode)
    logging.debug("Current user: %s, is anon: %s", current_user,
            current_user.is_anonymous)
    # Only login via tripcode if we're not claimed by someone else
    if not current_user.is_authenticated:
        anon_user = model.Identity.get_or_create_from_id('tripcode:' +
                hashed_tripcode, display=hashed_tripcode, handle=hashed_tripcode)
        logging.debug("Generated unauthenticated identity for %s: %s", tripcode,
                anon_user.id)
        login_user(anon_user)
        '''Update what current_user really points to'''
        request.user = anon_user

def hash_tripcode(value):
    """Parses a string and returns the tripcode-ified version"""
    tokens = value.split('#', 1)
    if len(tokens) == 1:
        return tokens[0]
    token_hash = hashlib.sha1()
    token_hash.update(tokens[0])
    token_hash.update(tokens[1])
    return tokens[0]+'$'+token_hash.hexdigest()

def randomHash():
    return ''.join([random.choice(string.ascii_letters+string.digits) for x in range(0, 10)])

def new_anon_user():
    code = 'Anonymous#' + randomHash()
    hashed = hash_tripcode(code)
    return model.Identity.get_or_create_from_id('tripcode:' + hashed,
            display=hashed,
            handle=hashed)

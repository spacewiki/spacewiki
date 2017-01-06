from spacewiki.cache import CACHE
from flask import render_template, g, current_app
import werkzeug
import re
import webpreview
import functools

@CACHE.memoize()
def unfurl_url(url):
    for k, v in CURRENT_UNFURLERS.iteritems():
        if k is not None:
            matches = k.match(url)
            current_app.logger.debug("unfurling %s with %s", url, v)
            if matches:
                return v(**matches.groupdict())
    return CURRENT_UNFURLERS[None](url)

def unfurl_default(url):
    title, desc, image = webpreview.web_preview(url)
    return render_template("_unfurl.html", title=title, desc=desc, image=image,
            url=url)

DEFAULT_UNFURLERS = {
    None: unfurl_default
}

def get_unfurlers():
    unfurlers = getattr(g, '_unfurlers', None)
    if unfurlers is None:
        g._unfurlers = DEFAULT_UNFURLERS
    return g._unfurlers

CURRENT_UNFURLERS = werkzeug.LocalProxy(get_unfurlers)

def unfurler(regex):
    """Decorator function to map a regex to a url unfurler"""
    def wrapper(f):
        DEFAULT_UNFURLERS[re.compile(regex)] = f
        return f
    return wrapper

@unfurler("https://.+\.?youtube.com/watch\?v=(?P<video>.+)")
def unfurl_youtube(video):
    title, desc, image = webpreview.web_preview("https://youtube.com/watch?v=%s"%(video))
    return render_template('_youtube.html', title=title, desc=desc, video=video)

"""Various special pages"""

from flask import Blueprint, render_template, request

from spacewiki import model

BLUEPRINT = Blueprint('specials', __name__)


@BLUEPRINT.route("/.search")
def search():
    """Searches page titles and generates a list of results"""
    query = request.args.get('q')
    pages = model.Page.select().where(model.Page.title.contains(query))
    return render_template('search.html', results=pages, query=query)


@BLUEPRINT.route("/.all-pages")
def allPages():
    pages = model.Page.select().order_by(model.Page.title)
    return render_template('all-pages.html',
                           pages=pages)

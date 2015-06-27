from flask import Blueprint, render_template, request

import model

bp = Blueprint('history', __name__)

@bp.route("/<slug>/revert", methods=['POST'])
def revert(slug):
    revision = request.form['revision']
    message = request.form['message']
    author = request.form['author']
    page = model.Page.get(slug=slug)
    oldRevision = model.Revision.get(page=page, id=revision)
    page.newRevision(oldRevision.body, "Revert to revision %s from %s: %s"
        %(oldRevision.id, oldRevision.timestamp, message), author)
    session = request.environ['beaker.session']
    session['author'] = author
    session.save()
    return redirect(url_for('pages.view', slug=page.slug))

@bp.route("/<slug>/history")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)

@bp.route('/<slug>/<start>..<end>')
def diff(slug, start, end):
    fromRev = model.Revision.get(id=start)
    toRev = model.Revision.get(id=end)
    return render_template('diff.html',
        fromRev=fromRev, toRev=toRev,
        diff=fromRev.diffTo(toRev), page=fromRev.page)

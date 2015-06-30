"""Routes for handling page history and reverts"""

from flask import Blueprint, render_template, request, url_for, redirect

from spacewiki import model

BLUEPRINT = Blueprint('history', __name__)


@BLUEPRINT.route("/<path:slug>/revert", methods=['POST'])
def revert(slug):
    """Handles reverting pages to previous revisions"""
    revision = request.form['revision']
    message = request.form['message']
    author = request.form['author']
    page = model.Page.get(slug=slug)
    old_revision = model.Revision.get(page=page, id=revision)
    page.newRevision(old_revision.body,
                     "Revert to revision %s from %s: %s" % (
                         old_revision.id,
                         old_revision.timestamp,
                         message
                     ),
                     author)
    session = request.environ['beaker.session']
    session['author'] = author
    session.save()
    return redirect(url_for('pages.view', slug=page.slug))


@BLUEPRINT.route("/<path:slug>/history")
def history(slug):
    """View the revision list of a page"""
    page = model.Page.get(slug=slug)
    return render_template('history.html', page=page)


@BLUEPRINT.route('/<path:slug>/<start>..<end>')
def diff(slug, start, end):  # pylint: disable=unused-argument
    """Renders the view for differences between page revisions"""
    from_rev = model.Revision.get(id=start)
    to_rev = model.Revision.get(id=end)
    return render_template('diff.html',
                           fromRev=from_rev, toRev=to_rev,
                           diff=from_rev.diffTo(to_rev), page=from_rev.page)

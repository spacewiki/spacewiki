from flask import Blueprint, current_app, request, render_template, make_response, jsonify
from flask_restful import Api, Resource, fields, marshal_with
from flask_login import current_user
import peewee
import logging

from spacewiki import model

BLUEPRINT = Blueprint('api', __name__)
API = Api(BLUEPRINT)

REVISION_FIELDS = {
    'body': fields.String,
    'id': fields.Integer,
    'timestamp': fields.DateTime,
    'author': fields.Nested({}),
    'message': fields.String,
    'rendered': fields.String(attribute='html')
}

class PageItem(Resource):
    @staticmethod
    def map_nav(p):
        return {'title': p.title, 'slug': '/'+p.slug}

    def diff(self, start, end):
        from_rev = model.Revision.get(id=start)
        to_rev = model.Revision.get(id=end)
        return {
            'fromRev': from_rev,
            'toRev': to_rev,
            'diff': from_rev.diffTo(to_rev),
            'page': from_rev.page
        }

    def post(self, slug=None):
        """Save a new Revision, creating a new Page if needed"""
        newslug = request.form.get('slug', None)
        title = request.form.get('title', None)
        if slug is None:
            slug = current_app.config['INDEX_PAGE']
        if slug != newslug:
            try:
                oldPage = model.Page.get(slug=newslug)
                logging.debug("Attempted rename of %s to %s", slug, newslug)
                return {'collision':"Cannot change URL! Something already exists there."}, 500
            except peewee.DoesNotExist:
                pass
        try:
            page = model.Page.get(slug=slug)
            logging.debug("Updating existing page: %s", page.slug)
            page.title = title
            page.slug = newslug
            page.save()
        except peewee.DoesNotExist:
            print "Saving '%s' at '%s'" %(title, slug)
            page = model.Page.create(title=title,
                                     slug=slug)
            logging.debug("Created new page: %s (%s)", page.title, page.slug)
        return page.newRevision(request.form['body'], request.form['message'],
                         current_user._get_current_object()).page

    def get(self, slug=None, revision=None):
        if slug is None:
            slug = current_app.config['INDEX_PAGE']

        last_page = None

        if revision is None:
            revision = model.Page.latestRevision(slug)
        else:
            revision = model.Revision.get(id=revision)

        last_page_slug = \
            model.Page.parsePreviousSlugFromRequest(
                request,
                current_app.config['INDEX_PAGE']
            )

        if last_page_slug is not None:
            try:
                last_page = model.Page.get(slug=last_page_slug)
            except peewee.DoesNotExist:
                pass

        if revision is not None:
            if last_page is not None and last_page != revision.page:
                revision.page.makeSoftlinkFrom(last_page)
            elif last_page is not None:
                current_app.logger.debug("Could not parse referrer: %s", last_page_slug)

            return revision.page
        else:
            return None, 404

API.add_resource(PageItem, '/', '/<path:slug>', '/<path:slug>@<int:revision>')

@API.representation('text/html')
def output_html(data, code, headers=None):
    conf = {
            'data': data,
            'status_code': code,
            'site_name': current_app.config['SITE_NAME'],
            'navigation': [],
            'current_user': current_user._get_current_object()
    }
    if code != 200:
        resp = make_response(render_template('error%s.html'%(code),
            app_config=conf), code)
    else:
        print repr(data)
        resp = make_response(render_template('render-%s.html'%(data.__class__.__name__),
            app_config=conf, data=data), code)
    resp.headers.extend(headers or {})
    return resp

@API.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(jsonify(data), code)
    resp.headers.extend(headers or {})
    return resp

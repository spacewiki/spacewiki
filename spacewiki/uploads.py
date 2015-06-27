from flask import current_app, Blueprint, render_template, request, redirect, url_for, Response
import logging
import peewee
from PIL import Image
import os
import tempfile
import werkzeug

import model

bp = Blueprint('uploads', __name__)

@bp.route("/<slug>/attach", methods=['GET'])
def upload(slug):
    """Show the file attachment form"""
    try:
        page = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=slug, slug=slug)
    return render_template('attach.html', page=page)

@bp.route("/<slug>/attach", methods=['POST'])
def attach(slug):
    """Handle saving a file upload"""
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Attaching file to existing page: %s", page.slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=slug, slug=slug)
        logging.debug("Created new page for attachment: %s", page.slug)
    file = request.files['file']
    fname = werkzeug.secure_filename(file.filename)
    tmpname = os.path.join(tempfile.mkdtemp(), "upload")
    with model.database.transaction():
        file.save(tmpname)
        page.attachUpload(tmpname, fname, current_app.config['UPLOAD_PATH'])
    return redirect(url_for('pages.view', slug=page.slug))

@bp.route("/<slug>/file/<fileslug>")
@bp.route("/<slug>/file/<fileslug>/<size>")
def get_attachment(slug, fileslug, size=None):
    attachment = model.Attachment.findAttachment(slug, fileslug)
    if attachment is None:
        logging.info("No attachment %s on %s", fileslug, slug)
        return Response(status=404)
    latestRevision = attachment.revisions[0]
    maxSize = None

    if size is not None:
        try:
            maxSize = max(0, int(size))
        except ValueError, e:
            maxSize = -1

    if maxSize is not None and maxSize <= 0:
        raise werkzeug.exceptions.NotFound()

    def generate(prefix):
        fname = model.Attachment.hashPath(latestRevision.sha,
            attachment.filename)
        if maxSize is not None:
            resizedFname = os.path.join(prefix, fname)+'-%s'%(maxSize)
            if not os.path.exists(resizedFname):
                img = Image.open(os.path.join(prefix, fname))
                w, h = img.size
                if w > h:
                  scale = float(maxSize) / w
                  w = maxSize
                  h = h * scale
                else:
                  scale = float(maxSize) / h
                  h = maxSize
                  w = w * scale
                img.thumbnail([w, h], Image.ANTIALIAS)
                img.save(resizedFname, format='png')
            f = open(resizedFname, 'r')
        else:
            f = open(os.path.join(prefix, fname))
        buf = f.read(2048)
        while buf:
            yield buf
            buf = f.read(2048)
    """FIXME: mimetype detection"""
    mimetype = 'image/png; charset=binary'
    return Response(generate(current_app.config['UPLOAD_PATH']), mimetype=mimetype)

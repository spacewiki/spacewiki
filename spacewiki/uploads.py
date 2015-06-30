"""Page attachments and uploads"""

from flask import current_app, Blueprint, render_template, request, redirect, url_for, Response
import logging
import peewee
from PIL import Image
import os
import tempfile
import werkzeug

from spacewiki import model

BLUEPRINT = Blueprint('uploads', __name__)


@BLUEPRINT.route("/<path:slug>/attach", methods=['GET'])
def upload(slug):
    """Show the file attachment form"""
    try:
        page = model.Page.get(slug=slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=slug, slug=slug)
    return render_template('attach.html', page=page)


@BLUEPRINT.route("/<path:slug>/attach", methods=['POST'])
def attach(slug):
    """Handle saving a file upload"""
    try:
        page = model.Page.get(slug=slug)
        logging.debug("Attaching file to existing page: %s", page.slug)
    except peewee.DoesNotExist:
        page = model.Page.create(title=slug, slug=slug)
        logging.debug("Created new page for attachment: %s", page.slug)
    uploaded_file = request.files['file']
    fname = werkzeug.secure_filename(uploaded_file.filename)
    tmpname = os.path.join(tempfile.mkdtemp(), "upload")
    with model.DATABASE.transaction():
        uploaded_file.save(tmpname)
        page.attachUpload(tmpname, fname, current_app.config['UPLOAD_PATH'])
    return redirect(url_for('pages.view', slug=page.slug))


@BLUEPRINT.route("/<path:slug>/file/<fileslug>")
@BLUEPRINT.route("/<path:slug>/file/<fileslug>/<size>")
def get_attachment(slug, fileslug, size=None):
    """Renders a file attachment, usually an image"""
    attachment = model.Attachment.findAttachment(slug, fileslug)
    if attachment is None:
        logging.info("No attachment %s on %s", fileslug, slug)
        return Response(status=404)
    latest_revision = attachment.revisions[0]
    max_size = None

    if size is not None:
        try:
            max_size = max(0, int(size))
        except ValueError:
            max_size = -1

    if max_size is not None and max_size <= 0:
        raise werkzeug.exceptions.NotFound()

    def generate(prefix):
        """Generator that streams a file's contents"""
        fname = model.Attachment.hashPath(latest_revision.sha,
                                          attachment.filename)
        if max_size is not None:
            resized_fname = os.path.join(prefix, fname)+'-%s' % (max_size)
            if not os.path.exists(resized_fname):
                img = Image.open(os.path.join(prefix, fname))
                width, height = img.size
                if width > height:
                    scale = float(max_size) / width
                    width = max_size
                    height = height * scale
                else:
                    scale = float(max_size) / height
                    height = max_size
                    width = width * scale
                img.thumbnail([width, height], Image.ANTIALIAS)
                img.save(resized_fname, format='png')
            upload_fh = open(resized_fname, 'r')
        else:
            upload_fh = open(os.path.join(prefix, fname))
        buf = upload_fh.read(2048)
        while buf:
            yield buf
            buf = upload_fh.read(2048)
    # FIXME: mimetype detection
    mimetype = 'image/png; charset=binary'
    return Response(generate(current_app.config['UPLOAD_PATH']), mimetype=mimetype)

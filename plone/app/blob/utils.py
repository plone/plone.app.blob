from zope.app.content_types import guess_content_type


def guessMimetype(data, filename=None):
    """ guess the mime-type from the given file-like object, optionally
        using the filename as a hint;  the current position in the file
        is tried to be preserved """
    pos = data.tell()
    if filename is None:    # mimetypes.guess_type expects a string
        filename = ''
    mimetype, enc = guess_content_type(filename, data.read(1 << 14))
    data.seek(pos)
    return str(mimetype)


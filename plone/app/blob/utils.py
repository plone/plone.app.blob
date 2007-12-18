from zope.component import getUtility
from zope.app.content_types import guess_content_type

from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool


def guessMimetype(data, filename=None):
    """ guess the mime-type from the given file-like object, optionally
        using the filename as a hint;  the current position in the file
        is tried to be preserved """
    pos = data.tell()
    mtr = getUtility(IMimetypesRegistryTool)
    if mtr is not None:
        d, f, mimetype = mtr(data.read(1 << 14), mimetype=None, filename=filename)
    else:
        mimetype, enc = guess_content_type(filename, data, mimetype=None)
    data.seek(pos)
    return str(mimetype)


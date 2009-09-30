from zope.app.content_types import guess_content_type
from Products.CMFCore.utils import getToolByName


from OFS.Image import getImageInfo

try:
    from PIL.Image import open as iopen
    hasPIL = True
except ImportError:
    hasPIL = False


def guessMimetype(data, filename=None, context=None):
    """ guess the mime-type from the given file-like object, optionally
        using the filename as a hint;  the current position in the file
        is tried to be preserved """
    pos = data.tell()
    contents = data.read(1 << 14)
    data.seek(pos)
    mtr = getToolByName(data, 'mimetypes_registry', None)
    if mtr is None and context is not None:
        mtr = getToolByName(context, 'mimetypes_registry', None)
    if mtr is not None:
        d, f, mimetype = mtr(contents, mimetype=None, filename=filename)
    else:
        if filename is None:    # mimetypes.guess_type expects a string
            filename = ''
        mimetype, enc = guess_content_type(filename, contents)
    return str(mimetype)



def getImageSize(img):
    """ determine the dimensions for the given image file """
    if hasPIL:
        try:
            return iopen(img).size
        except IOError:
            return None
    else:
        data = img.read(32)
        return getImageInfo(data)[1:]


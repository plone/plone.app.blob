from zope.component import queryUtility
from zope.contenttype import guess_content_type

from OFS.Image import getImageInfo
from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool

try:
    from PIL.Image import open as iopen
    hasPIL = True
except ImportError:
    hasPIL = False


def guessMimetype(data, filename=None):
    """ guess the mime-type from the given file-like object, optionally
        using the filename as a hint;  the current position in the file
        is tried to be preserved """
    pos = data.tell()
    mtr = queryUtility(IMimetypesRegistryTool)
    if mtr is not None:
        d, f, mimetype = mtr(data.read(1 << 14), mimetype=None, filename=filename)
    else:
        mimetype, enc = guess_content_type(filename or '', data.read(), default=None)
    data.seek(pos)
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

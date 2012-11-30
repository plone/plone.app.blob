# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface import file as atfile
from Products.ATContentTypes.interface import image as atimage
from Products.ATContentTypes.interface import news as atnews
from plone.app.blob.interfaces import IATBlobBlob, IATBlobFile, IATBlobImage, IATBlobNewsItem

# support for zope2-interfaces
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage
from Products.ATContentTypes.interfaces import IATNewsItem as Z2IATNewsItem

interfaces = {
    'Blob': [IATBlobBlob, atfile.IATFile, atfile.IFileContent],
    'File': [IATBlobFile, atfile.IATFile, atfile.IFileContent],
    'Image': [IATBlobImage, atimage.IATImage, atimage.IImageContent],
    'News Item': [IATBlobNewsItem, atnews.IATNewsItem],
}

z2interfaces = {
    'Blob': [Z2IATFile],
    'File': [Z2IATFile],
    'Image': [Z2IATImage],
    'News Item': [Z2IATNewsItem],
}


def markAs(obj, typename):
    for i in interfaces.get(typename, ()):
        alsoProvides(obj, i)
    z2 = z2interfaces.get(typename, None)
    if z2 is not None:
        implements = getattr(obj, '__implements__', [])
        obj.__implements__ = tuple(set(implements).union(z2))


def unmarkAs(obj, typename):
    for i in interfaces.get(typename, ()):
        noLongerProvides(obj, i)
    z2 = z2interfaces.get(typename, None)
    if z2 is not None:
        implements = getattr(obj, '__implements__', [])
        obj.__implements__ = tuple(set(implements) - set(z2))

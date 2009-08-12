# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface.file import IATFile, IFileContent
from Products.ATContentTypes.interface.image import IATImage, IImageContent
from plone.app.blob.interfaces import IATBlobBlob, IATBlobFile, IATBlobImage

# support for zope2-interfaces
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage


interfaces = {
    'Blob': [ IATBlobBlob, IATFile, IFileContent ],
    'File': [ IATBlobFile, IATFile, IFileContent ],
    'Image': [ IATBlobImage, IATImage, IImageContent ],
}

z2interfaces = {
    'Blob': [ Z2IATFile ],
    'File': [ Z2IATFile ],
    'Image': [ Z2IATImage ],
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

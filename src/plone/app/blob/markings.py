# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface.file import IATFile, IFileContent
from Products.ATContentTypes.interface.image import IATImage, IImageContent
from plone.app.blob.interfaces import IATBlobBlob, IATBlobFile, IATBlobImage


interfaces = {
    'Blob': [ IATBlobBlob, IATFile, IFileContent ],
    'File': [ IATBlobFile, IATFile, IFileContent ],
    'Image': [ IATBlobImage, IATImage, IImageContent ],
}


def markAs(obj, typename):
    for i in interfaces.get(typename, ()):
        alsoProvides(obj, i)

def unmarkAs(obj, typename):
    for i in interfaces.get(typename, ()):
        noLongerProvides(obj, i)


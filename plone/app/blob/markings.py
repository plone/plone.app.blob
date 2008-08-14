# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface.file import IATFile, IFileContent
from plone.app.blob.interfaces import IATBlobFile


interfaces = {
    'Blob': [ IATBlobFile, IATFile, IFileContent ],
    'File': [ IATBlobFile, IATFile, IFileContent ],
}


def markAs(obj, typename):
    for i in interfaces.get(typename, ()):
        alsoProvides(obj, i)

def ummarkAs(obj, typename):
    for i in interfaces.get(typename, ()):
        noLongerProvides(obj, i)


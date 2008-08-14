# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from zope.interface import alsoProvides, noLongerProvides
from Products.ATContentTypes.interface.file import IATFile, IFileContent
from plone.app.blob.interfaces import IATBlobFile


interfaces = {
    'File': [ IATBlobFile, IATFile, IFileContent ],
}


def markAs(obj, typename):
    alsoProvides(obj, *interfaces[typename])

def ummarkAs(obj, typename):
    for i in interfaces[typename]:
        noLongerProvides(obj, i)


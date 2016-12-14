# -*- coding: utf-8 -*-
# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.interfaces import IATImage
from Products.ATContentTypes.interfaces import IFileContent
from Products.ATContentTypes.interfaces import IImageContent
from plone.app.blob.interfaces import IATBlobBlob
from plone.app.blob.interfaces import IATBlobFile
from plone.app.blob.interfaces import IATBlobImage
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


interfaces = {
    'Blob': [IATBlobBlob, IATFile, IFileContent],
    'File': [IATBlobFile, IATFile, IFileContent],
    'Image': [IATBlobImage, IATImage, IImageContent],
}


def markAs(obj, typename):
    for i in interfaces.get(typename, ()):
        alsoProvides(obj, i)


def unmarkAs(obj, typename):
    for i in interfaces.get(typename, ()):
        noLongerProvides(obj, i)

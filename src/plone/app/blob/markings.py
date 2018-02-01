# -*- coding: utf-8 -*-
# convenience helpers to apply needed marker interfaces to blob-based content
# TODO: this could use named utilities to make it more pluggable

from plone.app.blob.interfaces import IATBlobBlob
from plone.app.blob.interfaces import IATBlobFile
from plone.app.blob.interfaces import IATBlobImage
from Products.ATContentTypes.interfaces import file as atfile
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage
from Products.ATContentTypes.interfaces import image as atimage
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


interfaces = {
    'Blob': [IATBlobBlob, atfile.IATFile, atfile.IFileContent],
    'File': [IATBlobFile, atfile.IATFile, atfile.IFileContent],
    'Image': [IATBlobImage, atimage.IATImage, atimage.IImageContent],
}

z2interfaces = {
    'Blob': [Z2IATFile],
    'File': [Z2IATFile],
    'Image': [Z2IATImage],
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

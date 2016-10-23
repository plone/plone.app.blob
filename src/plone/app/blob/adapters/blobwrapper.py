# -*- coding: utf-8 -*-
from plone.app.blob.field import ReuseBlob
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IBlobWrapper
from zope.component import adapts
from zope.interface import implementer


@implementer(IBlobbable)
class BlobbableBlobWrapper(object):
    """ adapter for BlobWrapper objects to work with blobs """
    adapts(IBlobWrapper)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        raise ReuseBlob(self.context.getBlob())

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()

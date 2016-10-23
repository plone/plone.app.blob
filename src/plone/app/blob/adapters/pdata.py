# -*- coding: utf-8 -*-
from OFS.Image import Pdata
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype
from StringIO import StringIO
from zope.component import adapts
from zope.interface import implementer


@implementer(IBlobbable)
class BlobbablePdata(object):
    """ adapter for Python file objects to work with blobs """
    adapts(Pdata)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        blobfile = blob.open('w')
        blobfile.write(self.context.data)
        chunk = self.context
        while chunk.next is not None:
            chunk = chunk.next
            blobfile.write(chunk.data)
        blobfile.close()

    def filename(self):
        """ see interface ... """
        return None

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(StringIO(self.context.data), None)

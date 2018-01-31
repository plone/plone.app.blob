# -*- coding: utf-8 -*-
from OFS.Image import Pdata
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype
from six import StringIO
from zope.component import adapter
from zope.interface import implementer


@adapter(Pdata)
@implementer(IBlobbable)
class BlobbablePdata(object):
    """ adapter for Python file objects to work with blobs """

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        with blob.open('w') as blobfile:
            blobfile.write(self.context.data)
            chunk = self.context
            while chunk.next is not None:
                chunk = chunk.next
                blobfile.write(chunk.data)

    def filename(self):
        """ see interface ... """
        return None

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(StringIO(self.context.data), None)

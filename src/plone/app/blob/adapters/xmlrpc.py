# -*- coding: utf-8 -*-
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype
from six.moves.xmlrpc_client import Binary
from zope.component import adapter
from zope.interface import implementer


@adapter(Binary)
@implementer(IBlobbable)
class BlobbableBinary(object):
    """ adapter for xmlrpclib Binary instance to work with blobs """

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        blobfile = blob.open('w')
        blobfile.writelines(self.context.data)
        blobfile.close()

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'filename', None)

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(self.context.data, self.filename())

from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable, IBlobWrapper
from plone.app.blob.field import ReuseBlob


class BlobbableBlobWrapper(object):
    """ adapter for BlobWrapper objects to work with blobs """
    implements(IBlobbable)
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

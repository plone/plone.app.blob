from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable, IBlobWrapper


class BlobbableBlobWrapper(object):
    """ adapter for BlobWrapper objects to work with blobs """
    implements(IBlobbable)
    adapts(IBlobWrapper)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        # do nothing except making sure the blob is already set (and the same)
        assert self.context.blob is blob

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()


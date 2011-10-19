from zope.interface import implements
from zope.component import adapts

from xmlrpclib import Binary

from plone.app.blob.interfaces import IBlobbable


class BlobbableBinary(object):
    """ adapter for xmlrpclib Binary instance to work with blobs """
    implements(IBlobbable)
    adapts(Binary)

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
        return 'application/octet-stream'

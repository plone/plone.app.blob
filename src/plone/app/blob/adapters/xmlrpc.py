from zope.interface import implements
from zope.component import adapts

from xmlrpclib import Binary

from plone.app.blob.interfaces import IBlobbable
#from plone.app.blob.utils import guessMimetype


class BlobbableBinary(object):
    """ adapter for xmlrpclib Binary instance to work with blobs """
    implements(IBlobbable)
    adapts(Binary)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
#        pos = self.context.tell()
#        self.context.seek(0)
        blobfile = blob.open('w')
        blobfile.writelines(self.context.data)
        blobfile.close()
#        self.context.seek(pos)

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'filename', None)

    def mimetype(self):
        """ see interface ... """
#        return guessMimetype(self.context, self.filename())
        return 'binary'


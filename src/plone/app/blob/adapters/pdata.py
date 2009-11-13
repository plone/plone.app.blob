from zope.interface import implements
from zope.component import adapts

from OFS.Image import Pdata
from StringIO import StringIO

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype


class BlobbablePdata(object):
    """ adapter for Python file objects to work with blobs """
    implements(IBlobbable)
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

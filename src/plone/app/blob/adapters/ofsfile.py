from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable, IOFSFile


class BlobbableOFSFile(object):
    """ adapter for OFS.File objects to work with blobs """
    implements(IBlobbable)
    adapts(IOFSFile)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        blobfile = blob.open('w')
        blobfile.write(str(self.context.data))  # TODO: use an iterator!!
        blobfile.close()

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'filename', '')

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()

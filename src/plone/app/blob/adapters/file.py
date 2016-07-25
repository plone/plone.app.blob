from zope.interface import implementer
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype


@implementer(IBlobbable)
class BlobbableFile(object):
    """ adapter for Python file objects to work with blobs """
    adapts(file)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        pos = self.context.tell()
        self.context.seek(0)
        blobfile = blob.open('w')
        blobfile.writelines(self.context)
        blobfile.close()
        self.context.seek(pos)

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'name', None)

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(self.context, self.filename())

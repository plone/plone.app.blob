from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IWebDavUpload
from plone.app.blob.utils import guessMimetype


class BlobbableWebDavUpload(object):
    """ adapter for WebDavUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IWebDavUpload)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        pos = self.context.file.tell()
        self.context.file.seek(0)
        blobfile = blob.open('w')
        blobfile.writelines(self.context.file)
        blobfile.close()
        self.context.file.seek(pos)

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        mimetype = self.context.mimetype
        if mimetype is None:
            mimetype = guessMimetype(self.context.file, self.filename())
        return mimetype

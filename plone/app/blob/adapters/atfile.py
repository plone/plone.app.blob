from zope.interface import implements
from zope.component import adapts

from Products.ATContentTypes.interface import IATFile

from plone.app.blob.interfaces import IBlobbable


class BlobbableATFile(object):
    """ adapter for ATFile objects to work with blobs """
    implements(IBlobbable)
    adapts(IATFile)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        blob.open('w').write(str(self.context))   # TODO: use an iterator!!

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()


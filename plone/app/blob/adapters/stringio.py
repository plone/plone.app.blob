from zope.interface import implements
from zope.component import adapts

from StringIO import StringIO

from plone.app.blob.interfaces import IBlobbable


class BlobbableStringIO(object):
    """ adapter for StringIO instance to work with blobs """
    implements(IBlobbable)
    adapts(StringIO)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        self.context.getvalue()

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'filename', None)

    def mimetype(self):
        """ see interface ... """
        return 'text/plain'


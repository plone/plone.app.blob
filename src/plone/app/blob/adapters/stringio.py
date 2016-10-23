# -*- coding: utf-8 -*-
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype
from StringIO import StringIO
from zope.component import adapts
from zope.interface import implementer


@implementer(IBlobbable)
class BlobbableStringIO(object):
    """ adapter for StringIO instance to work with blobs """
    adapts(StringIO)

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
        return getattr(self.context, 'filename', None)

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(self.context, self.filename())

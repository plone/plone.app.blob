# -*- coding: utf-8 -*-
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.utils import guessMimetype
from zope.component import adapter
from zope.interface import implementer


@adapter(file)
@implementer(IBlobbable)
class BlobbableFile(object):
    """ adapter for Python file objects to work with blobs """

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        pos = self.context.tell()
        self.context.seek(0)
        with blob.open('w') as blobfile:
            blobfile.writelines(self.context)
        self.context.seek(pos)

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'name', None)

    def mimetype(self):
        """ see interface ... """
        return guessMimetype(self.context, self.filename())

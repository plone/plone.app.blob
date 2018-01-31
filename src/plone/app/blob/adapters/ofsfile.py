# -*- coding: utf-8 -*-
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IOFSFile
from zope.component import adapter
from zope.interface import implementer


@adapter(IOFSFile)
@implementer(IBlobbable)
class BlobbableOFSFile(object):
    """ adapter for OFS.File objects to work with blobs """

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        with blob.open('w') as blobfile:
            blobfile.write(str(self.context.data))

    def filename(self):
        """ see interface ... """
        return getattr(self.context, 'filename', '')

    def mimetype(self):
        """ see interface ... """
        return self.context.getContentType()

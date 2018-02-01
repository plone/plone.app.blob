# -*- coding: utf-8 -*-
from plone.app.blob.adapters.atfile import BlobbableATFile
from Products.ATContentTypes.interfaces import IATImage
from zope.component import adapter


@adapter(IATImage)
class BlobbableATImage(BlobbableATFile):
    """ adapter for ATImage objects to work with blobs """

    def feed(self, blob):
        """ see interface ... """
        data = self.context.getImageAsFile()
        if data is None:
            return
        with blob.open('w') as blobfile:
            blobfile.write(data.read())

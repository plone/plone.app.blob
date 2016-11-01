# -*- coding: utf-8 -*-
from plone.app.blob.adapters.ofsfile import BlobbableOFSFile
from plone.app.blob.interfaces import IBlobbable
from Products.ATContentTypes.interface import IATFile
from zope.component import adapts
from zope.interface import implementer


@implementer(IBlobbable)
class BlobbableATFile(BlobbableOFSFile):
    """ adapter for ATFile objects to work with blobs """
    adapts(IATFile)

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

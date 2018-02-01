# -*- coding: utf-8 -*-
from plone.app.blob.adapters.ofsfile import BlobbableOFSFile
from plone.app.blob.interfaces import IBlobbable
from Products.ATContentTypes.interface import IATFile
from zope.component import adapter
from zope.interface import implementer


@adapter(IATFile)
@implementer(IBlobbable)
class BlobbableATFile(BlobbableOFSFile):
    """ adapter for ATFile objects to work with blobs """

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

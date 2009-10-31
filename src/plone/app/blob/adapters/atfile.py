from zope.interface import implements
from zope.component import adapts

from Products.ATContentTypes.interface import IATFile
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.adapters.ofsfile import BlobbableOFSFile


class BlobbableATFile(BlobbableOFSFile):
    """ adapter for ATFile objects to work with blobs """
    implements(IBlobbable)
    adapts(IATFile)

    def filename(self):
        """ see interface ... """
        return self.context.getFilename()

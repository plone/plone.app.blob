
from plone.app.blob.monkey import TemporaryFileWrapper
from plone.namedfile.interfaces import IStorage
from plone.namedfile.interfaces import NotStorable
from zope.interface import implementer


@implementer(IStorage)
class TemporaryFileWrapperStorage(object):

    def store(self, data, blob):
        if not isinstance(data, TemporaryFileWrapper):
            msg = 'Could not store data (not of TemporaryFileWrapper type)'
            raise NotStorable(msg)

        filename = getattr(data, 'name', None)
        if filename is not None:
            blob.consumeFile(filename)
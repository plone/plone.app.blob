from os.path import isfile
from shutil import copyfileobj
from os import name as os_name

from zope.interface import implements
from zope.component import adapts
from ZODB.blob import Blob

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IFileUpload
from plone.app.blob.utils import guessMimetype
from plone.app.blob.field import ReuseBlob


class BlobbableFileUpload(object):
    """ adapter for FileUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IFileUpload)

    def __init__(self, context):
        self.context = context
        self.__mimetype = guessMimetype(self.context, self.filename())

    def feed(self, blob):
        """ see interface ... """
        cached = getattr(self.context, 'blob', None)
        if cached is not None and isinstance(cached, Blob):
            raise ReuseBlob(cached)
        else:
            self.context.blob = blob
        filename = getattr(self.context, 'name', None)
        if os_name == 'nt' and filename is not None:
            # for now a copy is needed on windows...
            blobfile = blob.open('w')
            copyfileobj(self.context, blobfile)
            blobfile.close()
        elif filename is not None:
            assert isfile(filename), 'invalid file for blob: %s' % filename
            blob.consumeFile(filename)
        else:   # the cgi module only creates a tempfile for 1000+ bytes
            self.context.seek(0)    # just to be sure we copy everything...
            blobfile = blob.open('w')
            blobfile.write(self.context.read())
            blobfile.close()

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        return self.__mimetype

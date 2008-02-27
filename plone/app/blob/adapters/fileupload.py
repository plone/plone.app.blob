from os.path import isfile

from zope.interface import implements
from zope.component import adapts

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IFileUpload
from plone.app.blob.utils import guessMimetype


class BlobbableFileUpload(object):
    """ adapter for FileUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IFileUpload)

    def __init__(self, context):
        self.context = context
        self.__mimetype = guessMimetype(self.context, self.filename())

    def feed(self, blob):
        """ see interface ... """
        filename = getattr(self.context, 'name', None)
        if filename is not None:
            assert isfile(filename), 'invalid file for blob: %s' % filename
            self.context.close()
            blob.consumeFile(filename)
        else:   # the cgi module only creates a tempfile for 1000+ bytes
            self.context.seek(0)    # just to be sure we copy everything...
            blob.open('w').write(self.context.read())

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        return self.__mimetype


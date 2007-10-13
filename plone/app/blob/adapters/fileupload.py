from os.path import isfile

from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from zope.contenttype import guess_content_type

from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IFileUpload


class BlobbableFileUpload(object):
    """ adapter for FileUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IFileUpload)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        filename = getattr(self.context, 'name', None)
        if filename is not None:
            assert isfile(filename), 'invalid file for blob: %s' % filename
            blob.consumeFile(filename)
        else:   # the cgi module only creates a tempfile for 1000+ bytes
            self.context.seek(0)    # just to be sure we copy everything...
            blob.open('w').write(self.context.read())

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        filename = self.filename()
        body = iter(self.context)
        mtr = getUtility(IMimetypesRegistryTool)
        if mtr is not None:
            d, f, mimetype = mtr(body.read(1 << 14), mimetype=None, filename=filename)
        else:
            mimetype, enc = guess_content_type(filename, body, mimetype=None)
        return str(mimetype)


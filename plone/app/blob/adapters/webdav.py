from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from zope.contenttype import guess_content_type

from Products.MimetypesRegistry.interfaces import IMimetypesRegistryTool

from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IWebDavUpload


class BlobbableWebDavUpload(object):
    """ adapter for WebDavUpload objects to work with blobs """
    implements(IBlobbable)
    adapts(IWebDavUpload)

    def __init__(self, context):
        self.context = context

    def feed(self, blob):
        """ see interface ... """
        self.context.file.seek(0)   # reset the input
        blob.open('w').writelines(self.context.file)

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        mimetype = self.context.mimetype
        if mimetype is None:
            filename = self.filename()
            body = self.context.file
            mtr = getUtility(IMimetypesRegistryTool)
            if mtr is not None:
                d, f, mimetype = mtr(body.read(1 << 14), mimetype=None, filename=filename)
            else:
                mimetype, enc = guess_content_type(filename, body, mimetype=None)
            self.context.file.seek(0)   # reset the input
        return str(mimetype)


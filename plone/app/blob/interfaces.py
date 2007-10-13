from zope.interface import Interface
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class IATBlob(Interface):
    """ a chunk of binary data, i.e. a blob """

    title = schema.TextLine(title = _(u"Title"))

    blob = schema.Field(title = _(u"Blob"),
        description = _(u"Binary data, similar to a file in the filesystem"),
        required = True)


class IBlobbable(Interface):
    """ interface adapters for file-like objects must provide to be usable
        for blob fields """

    def feed(blob):
        """ store the file contents into the given blob, either be calling
            `consumeFile` or copying the contents in case no correspondig
            file object exists """

    def filename():
        """ return an associated filename, or `None` """

    def mimetype():
        """ return the mime type of the file contents if available, or
            `None` otherwise """


class IFileUpload(Interface):
    """ marker interface for ZPublisher.HTTPRequest.FileUpload class """


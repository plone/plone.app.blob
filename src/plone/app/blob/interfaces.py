# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from zope import schema
from zope.interface import Interface


class IATBlob(Interface):
    """ a chunk of binary data, i.e. a blob """

    title = schema.TextLine(title=_(u"Title"))

    blob = schema.Field(
        title=_(u"Blob"),
        description=_(u"Binary data, similar to a file in the filesystem"),
        required=True
    )


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


class IBlobWrapper(Interface):
    """ marker interface for the persistent wrapper class for zodb blobs """


class IBlobField(Interface):
    """ marker interface for blob-based archetypes field """


class IBlobImageField(IBlobField):
    """ marker interface for blob-based archetypes image field """


class IOFSFile(Interface):
    """ marker interface for OFS.Image.File class """


class IFileUpload(Interface):
    """ marker interface for ZPublisher.HTTPRequest.FileUpload class """


class IATBlobBlob(Interface):
    """ marker interface for sample blob subtype """


class IATBlobFile(Interface):
    """ marker interface for subtype mimicking the `ATFile` type """


class IATBlobImage(Interface):
    """ marker interface for subtype mimicking the `ATImage` type """


class IWebDavUpload(Interface):
    """ marker interface for webdav upload helper class """


class IBlobMaintenanceView(Interface):
    """ helper view for upgrade & maintenance tasks """

    def resetSubtypes(batch=1000):
        """ walk all catalog entries and reset sub-type markings """

    def updateTypeIndex(batch=1000):
        """ walk all catalog entries and update the 'Type' index """

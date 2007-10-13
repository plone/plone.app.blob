from zope.interface import Interface
from zope import schema
from Products.CMFPlone import PloneMessageFactory as _


class IATBlob(Interface):
    """ a chunk of binary data, i.e. a blob """

    title = schema.TextLine(title = _(u"Title"))

    blob = schema.Field(title = _(u"Blob"),
        description = _(u"Binary data, similar to a file in the filesystem"),
        required = True)


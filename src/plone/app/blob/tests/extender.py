from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from Products.ATContentTypes.interfaces import IATDocument, IATImage

from plone.app.blob.subtypes.image import ExtensionBlobField


class PageImageAdder(object):
    adapts(IATDocument)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField("image"),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


class ImageImageAdder(object):
    adapts(IATImage)
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField("new_image"),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

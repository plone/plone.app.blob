# -*- coding: utf-8 -*-
from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.subtypes.image import ExtensionBlobField
from Products.ATContentTypes.interfaces import IATDocument
from Products.ATContentTypes.interfaces import IATImage
from zope.component import adapter
from zope.interface import implementer


@adapter(IATDocument)
@implementer(ISchemaExtender)
class PageImageAdder(object):

    fields = [
        ExtensionBlobField('image'),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


@adapter(IATImage)
@implementer(ISchemaExtender)
class ImageImageAdder(object):

    fields = [
        ExtensionBlobField('new_image'),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

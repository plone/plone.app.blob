# -*- coding: utf-8 -*-
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.field import BlobField
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import FileWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.validation import V_REQUIRED
from zope.interface import implementer


class ExtensionBlobField(ExtensionField, BlobField):
    """ derivative of blobfield for extending schemas """


@implementer(ISchemaExtender)
class SchemaExtender(object):

    fields = [
        ExtensionBlobField(
            'file',
            required=True,
            primary=True,
            searchable=True,
            accessor='getFile',
            mutator='setFile',
            index_method='getIndexValue',
            languageIndependent=True,
            storage=AnnotationStorage(migrate=True),
            default_content_type='application/octet-stream',
            validators=(
                ('isNonEmptyFile', V_REQUIRED),
                ('checkFileMaxSize', V_REQUIRED),
            ),
            widget=FileWidget(
                label=_(u'label_file', default=u'File'),
                description=_(u''),
                show_content_type=False,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

# -*- coding: utf-8 -*-

from zope.interface import implements

from Acquisition import aq_base

from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageWidget, RichWidget
from Products.Archetypes.atapi import StringWidget, TextAreaWidget
from Products.Archetypes.atapi import StringField, TextField
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.blob.subtypes.image import ExtensionBlobField

class ExtensionTextField(ExtensionField, TextField):
    """ derivative of text for extending schemas """

class ExtensionStringField(ExtensionField, StringField):
    """ derivative of text for extending schemas """

class SchemaExtender(object):
    implements(ISchemaExtender)

    fields = [

        ExtensionTextField('text',
            required = False,
            searchable = True,
            primary = True,
            storage = AnnotationStorage(migrate=True),
            validators = ('isTidyHtmlWithCleanup',),
            #validators = ('isTidyHtml',),
            default_output_type = 'text/x-html-safe',
            widget = RichWidget(
                description = '',
                label = _(u'label_body_text', u'Body Text'),
                rows = 25,
                allow_file_upload = zconf.ATDocument.allow_document_upload)
            ),

        ExtensionBlobField('image',
            required = False,
            accessor = 'getImage',
            mutator = 'setImage',
            sizes = None,
            languageIndependent = True,
            storage = AnnotationStorage(migrate=True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            original_size = None,
            max_size = zconf.ATNewsItem.max_image_dimension,
            default_content_type = 'image/png',
            allowable_content_types = ('image/gif', 'image/jpeg', 'image/png'),
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkImageMaxSize', V_REQUIRED)),
            widget = ImageWidget(
                description = _(u'help_news_image',
                                default=u'Will be shown in the news listing, and in the news item itself. Image will be scaled to a sensible size.'),
                label= _(u'label_news_image', default=u'Image'),
                show_content_type = False)
            ),

        ExtensionStringField('imageCaption',
            required = False,
            searchable = True,
            widget = StringWidget(
                description = '',
                label = _(u'label_image_caption', default=u'Image Caption'),
                size = 40)
            ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

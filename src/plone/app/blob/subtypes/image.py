# -*- coding: utf-8 -*-
from Acquisition import aq_base
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.mixins import ImageFieldMixin
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageWidget
from Products.ATContentTypes.configuration import zconf
from Products.CMFPlone import PloneMessageFactory as _
from Products.validation import V_REQUIRED
from zope.interface import implementer


@implementer(IBlobImageField)
class ExtensionBlobField(ExtensionField, BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """

    def set(self, instance, value, refresh_exif=True, **kwargs):
        super(ExtensionBlobField, self).set(instance, value, **kwargs)
        self.fixAutoId(instance)
        if hasattr(instance, 'getEXIF'):
            # If the instance subclasses ATCTImageTransform we process the
            # metadata.
            # TODO: The EXIF functionality should not be dependent on ATCT
            instance.getEXIF(value, refresh=refresh_exif)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)


@implementer(ISchemaExtender)
class SchemaExtender(object):

    fields = [
        ExtensionBlobField(
            'image',
            required=True,
            primary=True,
            accessor='getImage',
            mutator='setImage',
            sizes=None,
            languageIndependent=True,
            storage=AnnotationStorage(migrate=True),
            swallowResizeExceptions=zconf.swallowImageResizeExceptions.enable,
            pil_quality=zconf.pil_config.quality,
            pil_resize_algo=zconf.pil_config.resize_algo,
            original_size=None,
            max_size=zconf.ATImage.max_image_dimension,
            default_content_type='image/png',
            allowable_content_types=('image/gif', 'image/jpeg', 'image/png'),
            validators=(
                ('isNonEmptyFile', V_REQUIRED),
                ('checkImageMaxSize', V_REQUIRED),
            ),
            widget=ImageWidget(
                label=_(u'label_image', default=u'Image'),
                description=_(u''),
                show_content_type=False,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

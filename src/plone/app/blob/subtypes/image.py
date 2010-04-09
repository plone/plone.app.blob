from zope.interface import implements
from Acquisition import aq_base
from Products.CMFPlone import PloneMessageFactory as _
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageWidget
from Products.ATContentTypes.configuration import zconf
from Products.validation import V_REQUIRED
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from plone.app.imaging.utils import getAllowedSizes
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField
from plone.app.blob.mixins import ImageFieldMixin


class ExtensionBlobField(ExtensionField, BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """
    implements(IBlobImageField)

    def set(self, instance, value, **kwargs):
        super(ExtensionBlobField, self).set(instance, value, **kwargs)
        self.fixAutoId(instance)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)


class SchemaExtender(object):
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField('image',
            required = True,
            primary = True,
            accessor = 'getImage',
            mutator = 'setImage',
            sizes = getAllowedSizes,
            languageIndependent = True,
            storage = AnnotationStorage(migrate=True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            max_size = zconf.ATImage.max_image_dimension,
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkImageMaxSize', V_REQUIRED)),
            widget = ImageWidget(label = _(u'label_image', default=u'Image'),
                                 description=_(u''),
                                 show_content_type = False,)),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

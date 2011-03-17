from Acquisition import Implicit, aq_base
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.validation import V_REQUIRED
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.field import BlobField, IndexMethodFix
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.imaging.utils import getAllowedSizes
from zope.app.component.hooks import getSite
from zope.interface import implements


class ExtensionBlobField(IndexMethodFix, ExtensionField, BlobField, ImageFieldMixin):
    """ derivative of blobfield for extending schemas """
    implements(IBlobImageField)

    def set(self, instance, value, **kwargs):
        super(ExtensionBlobField, self).set(instance, value, **kwargs)
        self.fixAutoId(instance)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)

    @property
    def sizes(self):
        return {
            'large'   : (768, 768),
            'preview' : (400, 400),
            'mini'    : (180, 135),
            'thumb'   : (128, 128),
            'wide'    : (325, 183),
            'tile'    :  (64, 64),
            'icon'    :  (32, 32),
            'listing' :  (16, 16),
        }


        #hardcoded sizes
        site = getSite()
        return getAllowedSizes(site)


class SchemaExtender(object):
    implements(ISchemaExtender)

    fields = [
        ExtensionBlobField('image',
            required = True,
            primary = True,
            default = '',
            accessor = 'getImage',
            mutator = 'setImage',
            languageIndependent = True,
            storage = AnnotationStorage(migrate=True),
            swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
            pil_quality = zconf.pil_config.quality,
            pil_resize_algo = zconf.pil_config.resize_algo,
            max_size = zconf.ATImage.max_image_dimension,
            validators = (('isNonEmptyFile', V_REQUIRED),
                          ('checkFileMaxSize', V_REQUIRED)),
            widget = ImageWidget(label = _(u'label_image', default=u'Image'),
                                 description=_(u''),
                                 show_content_type = False,))
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

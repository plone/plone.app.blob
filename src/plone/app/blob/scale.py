# -*- coding: utf-8 -*-
from Acquisition import aq_base
from logging import getLogger
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.utils import openBlob
from plone.app.imaging.interfaces import IImageScaleFactory
from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.imaging.traverse import DefaultImageScaleHandler
from plone.app.imaging.traverse import ImageScale
from ZODB.blob import Blob
from zope.component import adapter
from zope.interface import implementer


try:
    from plone.scale.scale import scaleImage
except ImportError:
    logger = getLogger('plone.app.blob')
    logger.warn('Warning: no Python Imaging Libraries (PIL) found. '
                'Can not scale images.')


@adapter(IBlobImageField)
@implementer(IImageScaleHandler)
class BlobImageScaleHandler(DefaultImageScaleHandler):
    """ handler for creating and storing scaled version of images in blobs """

    def retrieveScale(self, instance, scale):
        """ retrieve a scaled version of the image """
        field = self.context
        if scale is None:
            blob = field.getUnwrapped(instance)
            data = dict(id=field.getName(), blob=blob.getBlob(),
                        content_type=blob.getContentType(),
                        filename=blob.getFilename())
        else:
            fields = getattr(aq_base(instance), blobScalesAttr, {})
            scales = fields.get(field.getName(), {})
            data = scales.get(scale)
        if data is not None:
            blob = openBlob(data['blob'])
            # `updata_data` & friends (from `OFS`) should support file
            # objects, so we could use something like:
            #   ImageScale(..., data=blob.getIterator(), ...)
            # but it uses `len(data)`, so we'll stick with a string for now
            image = ImageScale(
                data['id'],
                data=blob.read(),
                content_type=data['content_type'],
                filename=data['filename'],
            )
            blob.close()
            return image.__of__(instance)
        return None

    def storeScale(self, instance, scale, **data):
        """ store a scaled version of the image """
        field = self.context
        fields = getattr(aq_base(instance), blobScalesAttr, {})
        scales = fields.setdefault(field.getName(), {})
        data['blob'] = Blob()
        blob = data['blob'].open('w')
        blob.write(data['data'])
        blob.close()
        del data['data']
        scales[scale] = data
        setattr(instance, blobScalesAttr, fields)


@implementer(IImageScaleFactory)
@adapter(IBlobImageField)
class BlobImageScaleFactory(object):
    """ adapter for image fields that allows generating scaled images """

    def __init__(self, field):
        self.field = field

    def create(self, context, **parameters):
        wrapper = self.field.get(context)
        if wrapper:
            blob = Blob()
            result = blob.open('w')
            _, format, dimensions = scaleImage(wrapper.getBlob().open('r'),
                                               result=result, **parameters)
            result.close()
            return blob, format, dimensions

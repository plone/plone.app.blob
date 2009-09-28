from zope.component import adapts
from zope.interface import implements
from Acquisition import aq_base
from ZODB.blob import Blob
from plone.app.imaging.traverse import DefaultImageScaleHandler, ImageScale
from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.config import blobScalesAttr


class BlobImageScaleHandler(DefaultImageScaleHandler):
    """ handler for creating and storing scaled version of images in blobs """
    implements(IImageScaleHandler)
    adapts(IBlobImageField)

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
            blob = data['blob'].open('r')
            # `updata_data` & friends (from `OFS`) should support file
            # objects, so we could use something like:
            #   ImageScale(..., data=blob.getIterator(), ...)
            # but it uses `len(data)`, so we'll stick with a string for now
            image = ImageScale(data['id'], data=blob.read(),
                content_type=data['content_type'], filename=data['filename'])
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

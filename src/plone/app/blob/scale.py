from zope.component import adapts
from zope.interface import implements
from Products.Archetypes.Field import Image
from Products.Archetypes.utils import shasattr
from plone.app.imaging.traverse import DefaultImageScaleHandler
from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.blob.interfaces import IBlobField


class BlobImageScaleHandler(DefaultImageScaleHandler):
    """ handler for creating and storing scaled version of images in blobs """
    implements(IImageScaleHandler)
    adapts(IBlobField)

    # XXX: fix me by storing things in blobs!!

    def getScale(self, instance, scale):
        """ return scaled and aq-wrapped version for given image data """
        field = self.context
        available = field.getAvailableSizes(instance)
        if scale is None:
            blob = field.getRaw(instance)
            filename = blob.getFilename()
            image = Image(field.getName(), title=filename,
                file=blob.getIterator(), content_type=blob.getContentType())
            image.filename = filename
        elif scale in available:
            width, height = available[scale]
            image = self.createScale(instance, scale, width, height)
        else:
            image = None
        if image is not None and shasattr(image, '__of__', acquire=True):
            image = image.__of__(instance)
        return image


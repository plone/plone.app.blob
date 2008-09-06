from zope.component import adapts
from zope.interface import implements
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
        if scale is None:
            return field.get(instance)
        available = field.getAvailableSizes(instance)
        if scale in available:
            width, height = available[scale]
            image = self.createScale(instance, scale, width, height)
            if image is not None:
                if shasattr(image, '__of__', acquire=True):
                    image = image.__of__(instance)
                return image
        return None


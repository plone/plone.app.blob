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
            try:
                image = self.createScale(instance, scale, width, height)
            except IOError:
                # It is possible that this handler is called when traversing to 
                # a browser view, page template or python script which is named 
                # in such a way that it conforms with the $fieldname_$scale image 
                # traversing convention and then ultimately ending up here.
                # 
                # An IOError("cannot identify image file") is then raised.
                #
                # An example is for example the Products.ARFFilePreview
                # 'file_preview' browser page.
                # 
                # Since we are not traversing to an image, we want to merely 
                # catch the error and return None.
                image = None
        else:
            image = None

        if image is not None and shasattr(image, '__of__', acquire=True):
            image = image.__of__(instance)
        return image



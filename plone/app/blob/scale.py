from zope.component import adapts
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from ZODB.blob import Blob
from Products.Archetypes.utils import shasattr
from plone.app.imaging.traverse import BaseImageScaleHandler
from plone.app.imaging.utils import getImageInfo
from plone.app.blob.interfaces import IBlobField
from plone.app.blob.field import BlobWrapper

class ScaleWrapper(BlobWrapper):
    """ Publish a scale """

    def __init__(self, instance, blob, content_type, filename, width, height):
        BlobWrapper.__init__(self, instance, blob, content_type, filename)
        self.width = width
        self.height = height

    def index_html(self, REQUEST=None, RESPONSE=None):
        """ make it directly viewable when entering the objects URL """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        RESPONSE.setHeader("Content-Type", self.content_type)
        RESPONSE.setHeader("Content-Length", self.get_size())
        return self.getIterator()


class BlobImageScaleHandler(BaseImageScaleHandler):
    """ handler for storing and retrieving scaled version of images in blobs """
    adapts(IBlobField)

    def getRawStream(self, instance):
        field = self.context
        return field.getRaw(instance).getIterator()

    def newStream(self):
        blob = Blob()
        return blob.open('w'), blob

    def storeScale(self, instance, scale, handle, content_type, width, height):
        """ store a scaled version of the image """
        field = self.context
        id = field.getName() + '_' + (scale or '')
        anno = IAnnotations(instance)
        anno['plone.app.blob.scale:%s'%id] = (handle, content_type, width, height)

    def retrieveScale(self, instance, scale):
        """ retrieve a scaled version of the image """
        field = self.context
        id = field.getName() + '_' + (scale or '')
        anno = IAnnotations(instance)
        try:
            blob, content_type, width, height = anno['plone.app.blob.scale:%s'%id]
        except KeyError:
            return None
        if scale is None:
            field = self.context
            blob = field.get(instance).getBlob()
        wrapper = ScaleWrapper(instance, blob, content_type, id, width, height)
        wrapper = wrapper.__of__(instance)
        return wrapper

    def removeScales(self, instance):
        """ remove all scales """
        field = self.context
        anno = IAnnotations(instance)
        id = 'plone.app.blob.scale:%s_' % field.getName()
        to_delete = [k for k in anno if k.startswith(id)]
        for k in to_delete:
            del anno[k]

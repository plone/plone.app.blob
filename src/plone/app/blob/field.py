# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Acquisition import aq_base
from Acquisition import Implicit
from ComputedAttribute import ComputedAttribute
from os import fstat
from persistent import Persistent
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.download import handleIfModifiedSince
from plone.app.blob.download import handleRequestRange
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IBlobField
from plone.app.blob.interfaces import IBlobImageField
from plone.app.blob.interfaces import IBlobWrapper
from plone.app.blob.interfaces import IWebDavUpload
from plone.app.blob.iterators import BlobStreamIterator
from plone.app.blob.mixins import ImageFieldMixin
from plone.app.blob.utils import getImageSize
from plone.app.blob.utils import getPILResizeAlgo
from plone.app.blob.utils import openBlob
from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from Products.Archetypes.atapi import FileWidget
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import ObjectField
from Products.Archetypes.atapi import PrimaryFieldMarshaller
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import contentDispositionHeader
from Products.CMFCore.permissions import View
from six import StringIO
from transaction import savepoint
from webdav.common import rfc1123_date
from ZODB.blob import Blob
from zope.interface import implementer

import six


@implementer(IWebDavUpload)
class WebDavUpload(object):
    """ helper class when handling webdav uploads;  the class is needed
        to be able to provide an adapter for this way of creating a blob """

    def __init__(self, file, filename=None, mimetype=None, context=None,
                 **kwargs):
        self.file = file
        if hasattr(aq_base(context), 'getFilename'):
            filename = context.getFilename() or filename
        self.filename = filename
        self.mimetype = mimetype
        self.kwargs = kwargs


class BlobMarshaller(PrimaryFieldMarshaller):

    def demarshall(self, instance, data, **kwargs):
        p = instance.getPrimaryField()
        mutator = p.getMutator(instance)
        mutator(WebDavUpload(**kwargs))


@implementer(IBlobWrapper)
class BlobWrapper(Implicit, Persistent):
    """ persistent wrapper for a zodb blob, also holding some metadata """

    security = ClassSecurityInfo()

    def __init__(self, content_type):
        self.blob = Blob()
        self.content_type = content_type
        self.filename = None

    @security.protected(View)
    def index_html(self, REQUEST=None, RESPONSE=None, charset='utf-8',
                   disposition='inline'):
        """ make it directly viewable when entering the objects URL """

        if REQUEST is None:
            REQUEST = self.REQUEST

        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        RESPONSE.setHeader('Last-Modified', rfc1123_date(self._p_mtime))
        RESPONSE.setHeader('Content-Type', self.getContentType())
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        if handleIfModifiedSince(self, REQUEST, RESPONSE):
            return ''

        length = self.get_size()
        RESPONSE.setHeader('Content-Length', length)

        filename = self.getFilename()
        if filename is not None:
            if not isinstance(filename, six.text_type):
                filename = six.text_type(filename, charset, errors='ignore')
            filename = IUserPreferredFileNameNormalizer(
                REQUEST,
            ).normalize(
                filename,
            )
            header_value = contentDispositionHeader(
                disposition=disposition,
                filename=filename,
            )
            # Add original filename in utf-8, ref to rfc2231
            RESPONSE.setHeader('Content-disposition', header_value)

        request_range = handleRequestRange(self, length, REQUEST, RESPONSE)
        return self.getIterator(**request_range)

    @security.private
    def setBlob(self, blob):
        """ set the contained blob object """
        self.blob = blob

    @security.private
    def getBlob(self):
        """ return the contained blob object """
        return self.blob

    @security.private
    def getIterator(self, **kw):
        """ return a filestream iterator object from the blob """
        return BlobStreamIterator(self.blob, **kw)

    @security.private
    def get_size(self):
        """ return the size of the blob """
        blob = openBlob(self.blob)
        size = fstat(blob.fileno()).st_size
        blob.close()
        return size

    __len__ = get_size

    def __nonzero__(self):
        # count as having a value unless we lack both data and a filename
        return bool(self.filename or len(self))

    @security.protected(View)
    def getSize(self):
        """ return image dimensions of the blob """
        # TODO: this should probably be cached...
        blob = openBlob(self.blob)
        size = getImageSize(blob)
        blob.close()
        return size

    @property
    @security.protected(View)
    def width(self):
        """ provide the image width as an attribute """
        width, height = self.getSize()
        return width

    @property
    @security.protected(View)
    def height(self):
        """ provide the image height as an attribute """
        width, height = self.getSize()
        return height

    @security.private
    def setContentType(self, value):
        """ set mimetype for this blob """
        # might be like: text/plain; charset='utf-8'
        value = str(value).split(';')[0].strip()
        self.content_type = value

    @security.public
    def getContentType(self):
        """ return mimetype for this blob """
        return self.content_type

    @security.private
    def setFilename(self, value):
        """ set filename for this blob """
        if isinstance(value, six.string_types):
            value = value[max(value.rfind('/'),
                              value.rfind('\\'),
                              value.rfind(':')) + 1:]
        self.filename = value

    @security.private
    def getFilename(self):
        """ return filename for this blob """
        return self.filename
    # compatibility methods

    def __str__(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        return openBlob(self.blob).read()

    data = ComputedAttribute(__str__, 0)


InitializeClass(BlobWrapper)


class ReuseBlob(Exception):
    """ exception indicating that a blob should be reused """


@implementer(IBlobField)
class BlobField(ObjectField):
    """ file field implementation based on zodb blobs """

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type': 'blob',
        'default': None,
        'primary': False,
        'widget': FileWidget,
        'default_content_type': 'application/octet-stream',
    })

    security = ClassSecurityInfo()

    @security.private
    def getUnwrapped(self, instance, **kwargs):
        return super(BlobField, self).get(instance, **kwargs)

    @security.private
    def get(self, instance, **kwargs):
        value = super(BlobField, self).get(instance, **kwargs)
        if getattr(value, '__of__', None) is not None:
            return value.__of__(instance)
        else:
            return value

    @security.private
    def set(self, instance, value, **kwargs):
        """ use input value to populate the blob and set the associated
            file name and mimetype.  the latter can be overridden by an
            option "mimetype" keyword argument """
        if value in ('DELETE_FILE', 'DELETE_IMAGE'):
            super(BlobField, self).unset(instance, **kwargs)
            return
        # create a new blob instead of modifying the old one to
        # achieve copy-on-write semantics
        blob = BlobWrapper(self.default_content_type)
        if isinstance(value, six.string_types):
            value = StringIO(value)     # simple strings cannot be adapted...
            setattr(value, 'filename', kwargs.get('filename', None))
        if value is not None:
            blobbable = IBlobbable(value)
            try:
                blobbable.feed(blob.getBlob())
            except ReuseBlob as exception:
                blob.setBlob(exception.args[0])     # reuse the given blob
            mimetype = kwargs.get('mimetype', None)
            if not mimetype:
                mimetype = blobbable.mimetype()
            if mimetype and mimetype != 'None':
                blob.setContentType(mimetype)
            blob.setFilename(kwargs.get('filename', blobbable.filename()))
        super(BlobField, self).set(instance, blob, **kwargs)
        # a transaction savepoint is created after setting the blob's value
        # in order to make it available at its temporary path (e.g. to index
        # pdfs etc using solr & tika within the same transaction)
        savepoint(optimistic=True)

    @security.private
    def fixAutoId(self, instance):
        """ if an explicit id was given and the instance still has the
            auto-generated one it should be renamed;  also see
            `_setATCTFileContent` in ATCT's `ATCTFileContent` class """
        if not self.primary:
            return
        filename = self.getFilename(instance)
        if filename is not None \
           and instance._isIDAutoGenerated(instance.getId()):
            request = instance.REQUEST
            req_id = request.form.get('id')
            if req_id and not instance._isIDAutoGenerated(req_id):
                return      # don't rename if an explicit id was given
            if hasattr(aq_base(instance), '_should_set_id_to_filename'):
                # ^^ BBB for ATContentTypes <2.0
                if not instance._should_set_id_to_filename(
                    filename,
                    request.form.get('title'),
                ):
                    return  # don't rename now if AT should do it from title
            if not isinstance(filename, six.text_type):
                filename = six.text_type(filename, instance.getCharset())
            filename = IUserPreferredFileNameNormalizer(
                request,
            ).normalize(
                filename,
            )
            if filename and not filename == instance.getId():
                # a file name was given, so the instance needs to be renamed...
                instance.setId(filename)

    @security.protected(View)
    def download(self, instance, REQUEST=None, RESPONSE=None):
        """ download the file (use default index_html) """
        return self.index_html(
            instance,
            REQUEST,
            RESPONSE,
            disposition='attachment',
        )

    @security.protected(View)
    def index_html(self, instance, REQUEST=None, RESPONSE=None, **kwargs):
        """ make it directly viewable when entering the objects URL """
        blob = self.get(instance, raw=True)  # TODO: why 'raw'?
        charset = instance.getCharset()
        return blob.index_html(
            REQUEST=REQUEST, RESPONSE=RESPONSE,
            charset=charset, **kwargs
        )

    @security.public
    def get_size(self, instance):
        """ return the size of the blob used for get_size in BaseObject """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.get_size()
        else:
            return 0

    @security.public
    def getContentType(self, instance, fromBaseUnit=True):
        """ return the mimetype associated with the blob data """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.getContentType()
        else:
            return 'application/octet-stream'

    @security.private
    def getFilename(self, instance, fromBaseUnit=True):
        """ return the file name associated with the blob data """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.getFilename()
        else:
            return None


registerField(
    BlobField,
    title='Blob',
    description='Used for storing files in blobs',
)

# convenience base classes for blob-aware file & image fields


class FileField(BlobField):
    """ base class for a blob-based file field """

    _properties = BlobField._properties.copy()
    _properties.update({
        'type': 'file',
    })


registerField(
    FileField,
    title='Blob-aware FileField',
    description='Used for storing files in blobs',
)


@implementer(IBlobImageField)
class ImageField(BlobField, ImageFieldMixin):
    """ base class for a blob-based image field """

    _properties = BlobField._properties.copy()
    _properties.update({
        'type': 'image',
        'original_size': None,
        'max_size': None,
        'sizes': None,
        'swallowResizeExceptions': False,
        'pil_quality': 88,
        'pil_resize_algo': getPILResizeAlgo(),
        'default_content_type': 'image/png',
        'allowable_content_types': ('image/gif', 'image/jpeg', 'image/png'),
        'widget': ImageWidget,
    })

    def set(self, instance, value, **kwargs):
        super(ImageField, self).set(instance, value, **kwargs)
        if hasattr(aq_base(instance), blobScalesAttr):
            delattr(aq_base(instance), blobScalesAttr)


registerField(
    ImageField,
    title='Blob-aware ImageField',
    description='Used for storing image in blobs',
)

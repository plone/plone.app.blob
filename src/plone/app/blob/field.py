from os import fstat

from zope.interface import implements

from StringIO import StringIO
from DateTime.DateTime import DateTime
from Acquisition import Implicit, aq_base
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
try:
    from App.class_init import InitializeClass
    InitializeClass     # keep pyflakes happy
except ImportError:
    from Globals import InitializeClass
from ZODB.blob import Blob
from ZODB.POSException import POSKeyError
from ZPublisher.HTTPRangeSupport import parseRange
from persistent import Persistent
from transaction import savepoint
from webdav.common import rfc1123_date

from Products.CMFCore.permissions import View
from Products.Archetypes.atapi import ObjectField, FileWidget
from Products.Archetypes.atapi import PrimaryFieldMarshaller
from Products.Archetypes.Registry import registerField
from Products.Archetypes.utils import contentDispositionHeader

from plone.i18n.normalizer.interfaces import IUserPreferredFileNameNormalizer
from plone.app.blob.interfaces import IBlobbable, IWebDavUpload, IBlobField
from plone.app.blob.interfaces import IBlobWrapper
from plone.app.blob.iterators import BlobStreamIterator, BlobStreamRangeIterator
from plone.app.blob.utils import getImageSize

class WebDavUpload(object):
    """ helper class when handling webdav uploads;  the class is needed
        to be able to provide an adapter for this way of creating a blob """
    implements(IWebDavUpload)

    def __init__(self, file, filename=None, mimetype=None, context=None, **kwargs):
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


class BlobWrapper(Implicit, Persistent):
    """ persistent wrapper for a zodb blob, also holding some metadata """
    implements(IBlobWrapper)

    security = ClassSecurityInfo()

    def __init__(self):
        self.blob = Blob()
        self.content_type = 'application/octet-stream'
        self.filename = None

    security.declarePrivate('setBlob')
    def setBlob(self, blob):
        """ set the contained blob object """
        self.blob = blob

    security.declarePrivate('getBlob')
    def getBlob(self):
        """ return the contained blob object """
        return self.blob

    security.declarePrivate('getIterator')
    def getIterator(self):
        """ return a filestream iterator object from the blob """
        return BlobStreamIterator(self.blob)

    security.declarePrivate('getRangeIterator')
    def getRangeIterator(self, start, end):
        """ return a filestream iterator object from the blob with range """
        return BlobStreamRangeIterator(self.blob, start=start, end=end)

    security.declareProtected(View, 'get_size')
    def get_size(self):
        """ return the size of the blob """
        try:
            blob = self.blob.open('r')
            size = fstat(blob.fileno()).st_size
            blob.close()
        except (POSKeyError, IOError):
            size = 0
        return size

    __len__ = get_size

    security.declareProtected(View, 'getSize')
    def getSize(self):
        """ return image dimensions of the blob """
        # TODO: this should probably be cached...
        blob = self.blob.open()
        size = getImageSize(blob)
        blob.close()
        return size

    security.declareProtected(View, 'width')
    @property
    def width(self):
        """ provide the image width as an attribute """
        width, height = self.getSize()
        return width

    security.declareProtected(View, 'height')
    @property
    def height(self):
        """ provide the image height as an attribute """
        width, height = self.getSize()
        return height

    security.declarePrivate('setContentType')
    def setContentType(self, value):
        """ set mimetype for this blob """
        value = str(value).split(';')[0].strip()    # might be like: text/plain; charset='utf-8'
        self.content_type = value

    security.declarePublic('getContentType')
    def getContentType(self):
        """ return mimetype for this blob """
        return self.content_type

    security.declarePrivate('setFilename')
    def setFilename(self, value):
        """ set filename for this blob """
        if isinstance(value, basestring):
            value = value[max(value.rfind('/'),
                              value.rfind('\\'),
                              value.rfind(':')) + 1:]
        self.filename = value

    security.declarePrivate('getFilename')
    def getFilename(self):
        """ return filename for this blob """
        return self.filename

    # compatibility methods

    def __str__(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        try:
            return self.blob.open().read()
        except (IOError, POSKeyError):
            return ''

    data = ComputedAttribute(__str__, 0)


InitializeClass(BlobWrapper)


class ReuseBlob(Exception):
    """ exception indicating that a blob should be reused """


class BlobField(ObjectField):
    """ file field implementation based on zodb blobs """
    implements(IBlobField)

    _properties = ObjectField._properties.copy()
    _properties.update({
        'type' : 'blob',
        'default' : None,
        'primary' : False,
        'widget' : FileWidget,
        'default_content_type' : 'application/octet-stream',
    })

    security = ClassSecurityInfo()

    security.declarePrivate('getUnwrapped')
    def getUnwrapped(self, instance, **kwargs):
        return super(BlobField, self).get(instance, **kwargs)

    security.declarePrivate('get')
    def get(self, instance, **kwargs):
        value = super(BlobField, self).get(instance, **kwargs)
        if getattr(value, '__of__', None) is not None:
            return value.__of__(instance)
        else:
            return value

    security.declarePrivate('set')
    def set(self, instance, value, **kwargs):
        """ use input value to populate the blob and set the associated
            file name and mimetype """
        if value == "DELETE_FILE":
            super(BlobField, self).unset(instance, **kwargs)
            return
        # create a new blob instead of modifying the old one to
        # achieve copy-on-write semantics.
        blob = BlobWrapper()
        if isinstance(value, basestring):
            # make StringIO from string, because StringIO may be adapted to Blobabble
            value = StringIO(value)
        if value is not None:
            blobbable = IBlobbable(value)
            try:
                blobbable.feed(blob.getBlob())
            except ReuseBlob, exception:
                blob.setBlob(exception.args[0])     # reuse the given blob
            blob.setContentType(blobbable.mimetype())
            blob.setFilename(blobbable.filename())
        super(BlobField, self).set(instance, blob, **kwargs)

    security.declarePrivate('fixAutoId')
    def fixAutoId(self, instance):
        """ if an explicit id was given and the instance still has the
            auto-generated one it should be renamed;  also see
            `_setATCTFileContent` in ATCT's `ATCTFileContent` class """
        filename = self.getFilename(instance)
        if filename is not None and instance._isIDAutoGenerated(instance.getId()):
            request = instance.REQUEST
            req_id = request.form.get('id')
            if req_id and not instance._isIDAutoGenerated(req_id):
                return      # don't rename if an explicit id was given
            if hasattr(aq_base(instance), '_should_set_id_to_filename'):
                # ^^ BBB for ATContentTypes <2.0
                if not instance._should_set_id_to_filename(filename, request.form.get('title')):
                    return      # don't rename now if AT should do it from title
            if not isinstance(filename, unicode):
                filename = unicode(filename, instance.getCharset())
            filename = IUserPreferredFileNameNormalizer(request).normalize(filename)
            if filename and not filename == instance.getId():
                # a file name was given, so the instance needs to be renamed...
                # a subtransaction is applied, since without it renaming
                # fails when the type is created using portal_factory
                savepoint(optimistic=True)
                instance.setId(filename)

    security.declareProtected(View, 'download')
    def download(self, instance, REQUEST=None, RESPONSE=None):
        """ download the file (use default index_html) """
        return self.index_html(instance, REQUEST, RESPONSE, disposition='attachment')

    security.declareProtected(View, 'index_html')
    def index_html(self, instance, REQUEST=None, RESPONSE=None, disposition='inline'):
        """ make it directly viewable when entering the objects URL """
        if REQUEST is None:
            REQUEST = instance.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE

        blob = self.getUnwrapped(instance, raw=True)    # TODO: why 'raw'?
        RESPONSE.setHeader('Last-Modified', rfc1123_date(instance._p_mtime))
        RESPONSE.setHeader('Content-Type', self.getContentType(instance))
        RESPONSE.setHeader('Accept-Ranges', 'bytes')

        if self._if_modified_since_request_handler(
            instance, REQUEST, RESPONSE):
            return ''

        RESPONSE.setHeader("Content-Length", blob.get_size())

        filename = self.getFilename(instance)
        if filename is not None:
            filename = IUserPreferredFileNameNormalizer(REQUEST).normalize(
                unicode(filename, instance.getCharset()))
            header_value = contentDispositionHeader(
                disposition=disposition,
                filename=filename)
            RESPONSE.setHeader("Content-disposition", header_value)

        iterator = self._range_request_handler(
            instance, blob, REQUEST, RESPONSE)
        if iterator is None:
            iterator = blob.getIterator()
        for data in iterator:
            RESPONSE.write(data)
        return ''

    def _if_modified_since_request_handler(
        self, instance, REQUEST, RESPONSE):
        # HTTP If-Modified-Since header handling: return True if
        # we can handle this request by returning a 304 response
        header=REQUEST.get_header('If-Modified-Since', None)
        if header is not None:
            header=header.split( ';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            # This happens to be what RFC2616 tells us to do in the face of an
            # invalid date.
            try:    mod_since=long(DateTime(header).timeTime())
            except: mod_since=None
            if mod_since is not None:
                if instance._p_mtime:
                    last_mod = long(instance._p_mtime)
                else:
                    last_mod = long(0)
                if last_mod > 0 and last_mod <= mod_since:
                    RESPONSE.setStatus(304)
                    return True

    def _range_request_handler(
        self, instance, blob, REQUEST, RESPONSE):
        # check if we have a range in the request
        ranges = None
        range = REQUEST.get_header('Range', None)
        request_range = REQUEST.get_header('Request-Range', None)
        if request_range is not None:
            # Netscape 2 through 4 and MSIE 3 implement a draft version
            # Later on, we need to serve a different mime-type as well.
            range = request_range
        if_range = REQUEST.get_header('If-Range', None)

        if range is not None:
            ranges = parseRange(range)

            if if_range is not None:
                # Only send ranges if the data isn't modified, otherwise send
                # the whole object. Support both ETags and Last-Modified dates!
                if len(if_range) > 1 and if_range[:2] == 'ts':
                    # ETag:
                    if if_range != instance.http__etag():
                        # Modified, so send a normal response. We delete
                        # the ranges, which causes us to skip to the 200
                        # response.
                        ranges = None
                else:
                    # Date
                    date = if_range.split( ';')[0]
                    try: mod_since=long(DateTime(date).timeTime())
                    except: mod_since=None
                    if mod_since is not None:
                        if instance._p_mtime:
                            last_mod = long(instance._p_mtime)
                        else:
                            last_mod = long(0)
                        if last_mod > mod_since:
                            # Modified, so send a normal response. We delete
                            # the ranges, which causes us to skip to the 200
                            # response.
                            ranges = None
                RESPONSE.setHeader('Accept-Ranges', 'bytes')
    
            if ranges and len(ranges) == 1:
                [(start, end)] = ranges
                iterator = blob.getRangeIterator(start=start, end=end)
                size = end - start
                RESPONSE.setHeader('Content-Length', size)
                RESPONSE.setHeader(
                    'Content-Range',
                    'bytes %d-%d/%d' % (start, end - 1, len(iterator)))
                RESPONSE.setStatus(206) # Partial content
                return iterator

    security.declarePublic('get_size')
    def get_size(self, instance):
        """ return the size of the blob used for get_size in BaseObject """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.get_size()
        else:
            return 0

    security.declarePublic('getContentType')
    def getContentType(self, instance, fromBaseUnit=True):
        """ return the mimetype associated with the blob data """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.getContentType()
        else:
            return 'application/octet-stream'

    security.declarePrivate('getFilename')
    def getFilename(self, instance, fromBaseUnit=True):
        """ return the file name associated with the blob data """
        blob = self.getUnwrapped(instance)
        if blob is not None:
            return blob.getFilename()
        else:
            return None


registerField(BlobField, title='Blob',
              description='Used for storing files in blobs')


class IndexMethodFix:
    """ archetypes.schemaextender's `getIndexAccessor` is currently broken
        wrt to the `index_method` schema attribute, so until this is fixed
        upstream we need to override the method in order to be able to use
        a custom indexer;  to do so mix this in before `ExtensionField` """

    def getIndexAccessor(self, instance):
        """ return the index accessor """
        name = getattr(self, 'index_method', None)
        if name is not None:
            return getattr(instance, name)
        else:
            return super(IndexMethodFix, self).getIndexAccessor(instance)

from logging import getLogger
from zope.interface import implements
from zope.lifecycleevent import ObjectCreatedEvent, ObjectModifiedEvent
from zope.event import notify

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from ZODB.POSException import ConflictError
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
try:
    from Products.LinguaPlone.public import registerType
    registerType        # make pyflakes happy...
except ImportError:
    from Products.Archetypes.atapi import registerType
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.MimetypesRegistry.common import MimeTypeException
from Products.GenericSetup.interfaces import IDAVAware

from plone.app.imaging.interfaces import IImageScaleHandler
from plone.app.blob.interfaces import IATBlob, IATBlobFile, IATBlobImage
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobMarshaller
from plone.app.blob.mixins import ImageMixin
from plone.app.blob.markings import markAs

ATBlobSchema = ATContentTypeSchema.copy()
ATBlobSchema['title'].storage = AnnotationStorage()
# titles not required for blobs, because we'll use the filename if missing
ATBlobSchema['title'].required = False

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)
ATBlobSchema.registerLayer('marshall', BlobMarshaller())


try:
    from Products.CMFCore.CMFCatalogAware import WorkflowAware
    WorkflowAware       # make pyflakes happy...
    # CMF 2.2 takes care of raising object events for old-style factories
    hasCMF22 = True
except ImportError:
    hasCMF22 = False


def addATBlob(container, id, subtype='Blob', **kwargs):
    """ extended at-constructor copied from ClassGen.py """
    obj = ATBlob(id)
    if subtype is not None:
        markAs(obj, subtype)    # mark with interfaces needed for subtype
    if not hasCMF22:
        notify(ObjectCreatedEvent(obj))
    container._setObject(id, obj, suppress_events=hasCMF22)
    obj = container._getOb(id)
    if hasCMF22:
        obj.manage_afterAdd(obj, container)
    obj.initializeArchetype(**kwargs)
    if not hasCMF22:
        notify(ObjectModifiedEvent(obj))
    return obj.getId()


def addATBlobFile(container, id, **kwargs):
    return addATBlob(container, id, subtype='File', **kwargs)


def addATBlobImage(container, id, **kwargs):
    return addATBlob(container, id, subtype='Image', **kwargs)


class ATBlob(ATCTFileContent, ImageMixin):
    """ a chunk of binary data """
    implements(IATBlob, IDAVAware)

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    title = ATFieldProperty('title')
    summary = ATFieldProperty('description')

    security = ClassSecurityInfo()
    cmf_edit_kws = ('file', )

    security.declareProtected(View, 'index_html')

    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline or as an attachment """
        field = self.getPrimaryField()
        if IATBlobImage.providedBy(self):
            return field.index_html(self, REQUEST, RESPONSE)
        elif field.getContentType(self) in ATFile.inlineMimetypes:
            return field.index_html(self, REQUEST, RESPONSE)
        else:
            return field.download(self, REQUEST, RESPONSE)
    # helper & explicit accessor and mutator methods

    security.declarePrivate('getBlobWrapper')

    def getBlobWrapper(self):
        """ return wrapper class containing the actual blob """
        accessor = self.getPrimaryField().getAccessor(self)
        return accessor()

    security.declareProtected(View, 'getFile')

    def getFile(self, **kwargs):
        """ archetypes.schemaextender (wisely) doesn't mess with classes,
            so we have to provide our own accessor """
        return self.getBlobWrapper()

    security.declareProtected(ModifyPortalContent, 'setFile')

    def setFile(self, value, **kwargs):
        """ set the file contents and possibly also the id """
        mutator = self.getField('file').getMutator(self)
        mutator(value, **kwargs)

    def _should_set_id_to_filename(self, filename, title):
        """ If title is blank, have the caller set my ID to the
            uploaded file's name. """
        # When the title is blank, sometimes the filename is returned
        return filename == title or not title
    # index accessor using portal transforms to provide index data

    security.declarePrivate('getIndexValue')

    def getIndexValue(self, mimetype='text/plain'):
        """ an accessor method used for indexing the field's value
            XXX: the implementation is mostly based on archetype's
            `FileField.getIndexable` and rather naive as all data gets
            loaded into memory if a suitable transform was found.
            this should probably use `plone.transforms` in the future """
        field = self.getPrimaryField()
        source = field.getContentType(self)
        transforms = getToolByName(self, 'portal_transforms')
        if transforms._findPath(source, mimetype) is None:
            return ''
        value = str(field.get(self))
        filename = field.getFilename(self)
        try:
            return str(transforms.convertTo(mimetype, value,
                mimetype=source, filename=filename))
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            getLogger(__name__).exception('exception while trying to convert '
               'blob contents to "text/plain" for %r', self)
    # compatibility methods when used as ATFile replacement

    security.declareProtected(View, 'get_data')

    def get_data(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        return str(self.getBlobWrapper())

    data = ComputedAttribute(get_data, 1)

    def __str__(self):
        """ return data as a string;  this is highly inefficient as it
            loads the complete blob content into memory, but the method
            is unfortunately still used here and there... """
        if IATBlobImage.providedBy(self):
            return self.getPrimaryField().tag(self)
        else:
            return self.get_data()

    def __repr__(self):
        """ try to mimic the the old file and image types from ATCT
            for improved test compatibility """
        res = super(ATBlob, self).__repr__()
        if IATBlobFile.providedBy(self):
            res = res.replace(ATBlob.__name__, 'ATFile', 1)
        elif IATBlobImage.providedBy(self):
            res = res.replace(ATBlob.__name__, 'ATImage', 1)
        return res

    security.declareProtected(ModifyPortalContent, 'setFilename')

    def setFilename(self, value, key=None):
        """ convenience method to set the file name on the field """
        self.getBlobWrapper().setFilename(value)

    security.declareProtected(ModifyPortalContent, 'setFormat')

    def setFormat(self, value):
        """ convenience method to set the mime-type """
        self.getBlobWrapper().setContentType(value)

    security.declarePublic('getIcon')

    def getIcon(self, relative_to_portal=False):
        """ calculate an icon based on mime-type """
        contenttype = self.getBlobWrapper().getContentType()
        mtr = getToolByName(self, 'mimetypes_registry', None)
        try:
            mimetypeitem = mtr.lookup(contenttype)
        except MimeTypeException:
            mimetypeitem = None
        if mimetypeitem is None or mimetypeitem == ():
            return super(ATBlob, self).getIcon(relative_to_portal)
        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName(self, 'portal_url')
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon

    security.declarePrivate('cmf_edit')

    def cmf_edit(self, precondition='', file=None, title=None, **kwargs):
        # implement cmf_edit for image and file distinctly
        primary_field_name = self.getPrimaryField().getName()
        if file is not None and primary_field_name == 'image':
            self.setImage(file)
        elif file is not None and primary_field_name == 'file':
            self.setFile(file)
        if title is not None:
            self.setTitle(title)
        if kwargs:
            self.edit(**kwargs)
        else:
            self.reindexObject()
    # compatibility methods when used as ATImage replacement

    def __bobo_traverse__(self, REQUEST, name):
        """ helper to access image scales the old way during
            `unrestrictedTraverse` calls """
        if isinstance(REQUEST, dict):
            if '_' in name:
                fieldname, scale = name.split('_', 1)
            else:
                fieldname, scale = name, None
            field = self.getField(fieldname)
            handler = IImageScaleHandler(field, None)
            if handler is not None:
                image = handler.getScale(self, scale)
                if image is not None:
                    return image
        return super(ATBlob, self).__bobo_traverse__(REQUEST, name)

registerType(ATBlob, packageName)

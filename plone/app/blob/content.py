from zope.interface import implements

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.Archetypes.atapi import Schema, AnnotationStorage
from Products.Archetypes.atapi import registerType, FileWidget
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.MimetypesRegistry.common import MimeTypeException
from Products.validation import V_REQUIRED

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobField, BlobMarshaller


ATBlobSchema = ATContentTypeSchema.copy() + Schema((
    BlobField('file',
        required = True,
        primary = True,
        searchable = True,
        default = '',
        accessor = 'getFile',
        mutator = 'setFile',
        languageIndependent = True,
        storage = AnnotationStorage(migrate=True),
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkFileMaxSize', V_REQUIRED)),
        widget = FileWidget(label = _(u'label_file', default=u'File'),
                            description=_(u''),
                            show_content_type = False,)),
))
ATBlobSchema['title'].storage = AnnotationStorage()

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)
ATBlobSchema.registerLayer('marshall', BlobMarshaller())


class ATBlob(ATCTFileContent):
    """ a chunk of binary data """
    implements(IATBlob)

    __implements__ = ATCTFileContent.__implements__, IATFile

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    security  = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline """
        field = self.getPrimaryField()
        return field.download(self, REQUEST, RESPONSE)

    # helper & explicit accessor and mutator methods

    security.declarePrivate('getBlobWrapper')
    def getBlobWrapper(self):
        """ return wrapper class containing the actual blob """
        return self.getField('file').get(self)

    security.declareProtected(View, 'getFile')
    def getFile(self, **kwargs):
        """ archetypes.schemaextender (wisely) doesn't mess with classes,
            so we have to provide our own accessor """
        return self.getBlobWrapper()

    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """ set the file contents and possibly also the id """
        mutator = self.getField('file').set(self, value, **kwargs)

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
        return self.get_data()

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
        except MimeTypeException, msg:
            mimetypeitem = None
        if mimetypeitem is None:
            return super(ATBlob, self).getIcon(relative_to_portal)
        icon = mimetypeitem[0].icon_path
        if not relative_to_portal:
            utool = getToolByName( self, 'portal_url' )
            icon = utool(relative=1) + '/' + icon
            while icon[:1] == '/':
                icon = icon[1:]
        return icon


registerType(ATBlob, packageName)


from zope.interface import implements

from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
from Products.Archetypes.atapi import registerType
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.ATContentTypes.interfaces import IATFile
from Products.ATContentTypes.content.base import ATCTFileContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobMarshaller


ATBlobSchema = ATContentTypeSchema.copy() + Schema(marshall = BlobMarshaller())
ATBlobSchema['title'].storage = AnnotationStorage()

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)


class ATBlob(ATCTFileContent):
    """ a chunk of binary data """
    implements(IATBlob)

    __implements__ = ATCTFileContent.__implements__, IATFile

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    title = ATFieldProperty('title')
    summary = ATFieldProperty('description')

    security  = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline """
        field = self.getPrimaryField()
        return field.index_html(self, REQUEST, RESPONSE)

    # helper & explicit accessor and mutator methods

    security.declarePrivate('getBlobWrapper')
    def getBlobWrapper(self):
        """ return wrapper class containing the actual blob """
        accessor = self.getField('file').getAccessor(self)
        return accessor()

    security.declareProtected(View, 'getFile')
    def getFile(self):
        """ archetypes.schemaextender (wisely) doesn't mess with classes,
            so we have to provide our own accessor """
        return self.getBlobWrapper()

    security.declareProtected(ModifyPortalContent, 'setFile')
    def setFile(self, value, **kwargs):
        """ set the file contents and possibly also the id """
        mutator = self.getField('file').getMutator(self)
        mutator(value, **kwargs)

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

    security.declareProtected(ModifyPortalContent, 'setFormat')
    def setFormat(self, value):
        """ convenience method to set the mime-type """
        self.getBlobWrapper().setContentType(value)


registerType(ATBlob, packageName)


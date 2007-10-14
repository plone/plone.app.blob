from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ATFieldProperty
from Products.Archetypes.atapi import registerType
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.base import ATCTContent
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobMarshaller


ATBlobSchema = ATContentTypeSchema.copy() + Schema(marshall = BlobMarshaller())
ATBlobSchema['title'].storage = AnnotationStorage()

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)


class ATBlob(ATCTContent):
    """ a chunk of binary data """
    implements(IATBlob)

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


registerType(ATBlob, packageName)


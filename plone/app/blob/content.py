from zope.interface import implements

from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from Products.ATContentTypes.content import base
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobField, BlobMarshaller


ATBlobSchema = ATContentTypeSchema.copy() + atapi.Schema((
    BlobField('blob',
        required = True,
        primary = True,
        searchable = True,
        languageIndependent = True,
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkFileMaxSize', V_REQUIRED)),
        widget = atapi.FileWidget(label = _(u'label_file', default=u'File'),
                            description=_(u''),
                            show_content_type = False,)),
    ), marshall = BlobMarshaller())

ATBlobSchema['title'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(ATBlobSchema, folderish=False, moveDiscussion=False)


class ATBlob(base.ATCTContent):
    """ a chunk of binary data """
    implements(IATBlob)

    portal_type = 'Blob'
    _at_rename_after_creation = True
    schema = ATBlobSchema

    title = atapi.ATFieldProperty('title')
    summary = atapi.ATFieldProperty('description')

    security  = ClassSecurityInfo()

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST, RESPONSE):
        """ download the file inline """
        field = self.getPrimaryField()
        return field.index_html(self, REQUEST, RESPONSE)


atapi.registerType(ATBlob, packageName)


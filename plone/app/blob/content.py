from zope.interface import implements

from Products.Archetypes import atapi
from Products.validation import V_REQUIRED

from Products.ATContentTypes.content import base
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.config import packageName



ATBlobSchema = ATContentTypeSchema.copy() + atapi.Schema((
    atapi.FileField('blob',
        required = True,
        primary = True,
        searchable = True,
        languageIndependent = True,
        storage = atapi.AnnotationStorage(migrate=True),
        validators = (('isNonEmptyFile', V_REQUIRED),
                      ('checkFileMaxSize', V_REQUIRED)),
        widget = atapi.FileWidget(label = _(u'label_file', default=u'File'),
                            description=_(u''),
                            show_content_type = False,)),
    ), marshall=atapi.PrimaryFieldMarshaller())

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


atapi.registerType(ATBlob, packageName)


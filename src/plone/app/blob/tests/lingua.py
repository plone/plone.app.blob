# -*- coding: utf-8 -*-
from plone.app.blob.config import packageName
from plone.app.blob.field import BlobField
from Products.Archetypes.atapi import StringField
from Products.CMFPlone import PloneMessageFactory as _
from Products.LinguaPlone.public import BaseContent
from Products.LinguaPlone.public import BaseSchema
from Products.LinguaPlone.public import FileWidget
from Products.LinguaPlone.public import registerType
from Products.LinguaPlone.public import Schema


BlobelFishSchema = BaseSchema.copy() + Schema((

    BlobField(
        name='guide',
        primary=True,
        languageIndependent=True,
        widget=FileWidget(label=_(u'label_file', default=u'File'),
                          description=_(u''), )),

    StringField(
        name='teststr',
        languageIndependent=True, ),

))


class BlobelFish(BaseContent):
    """ a multilingual fish """

    schema = BlobelFishSchema
    _at_rename_after_creation = True


registerType(BlobelFish, packageName)

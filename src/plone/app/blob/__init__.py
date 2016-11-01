# -*- coding: utf-8 -*-
from plone.app.blob.config import packageName
from plone.app.blob.config import permissions


def initialize(context):
    """ initializer called when used as a zope2 product """

    # setup non-anonymous file uploads
    from plone.app.blob import monkey
    monkey.__name__     # make pyflakes happy...

    # initialize portal content
    from plone.app.blob import content
    content.__name__    # make pyflakes happy...

    from Products.CMFCore import utils
    from Products.Archetypes import atapi
    from Products.ATContentTypes import permission as atct

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(packageName), packageName)
    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit(
            '{0}: {1}'.format(packageName, atype.portal_type),
            content_types=(atype, ),
            permission=permissions[atype.portal_type],
            extra_constructors=(constructor, ),
        ).initialize(context)

    replacement_types = (
        ('File', content.addATBlobFile),
        ('Image', content.addATBlobImage),
    )
    for name, constructor in replacement_types:
        utils.ContentInit(
            '{0}: {1}'.format(packageName, name),
            content_types=(content.ATBlob, ),
            permission=atct.permissions.get(name),
            extra_constructors=(constructor, ),
        ).initialize(context)

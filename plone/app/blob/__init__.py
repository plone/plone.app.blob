from Products.Archetypes import atapi
from Products.CMFCore import utils

from plone.app.blob.config import packageName, permissions


def initialize(context):
    """ initializer called when used as a zope2 product """

    # setup non-anonymous file uploads
    import monkey

    # initialize portal content
    import content
    content = content   # make pyflakes happy...

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(packageName), packageName)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (packageName, atype.portal_type),
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)


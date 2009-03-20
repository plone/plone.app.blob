from plone.app.blob.config import packageName, permissions


def initialize(context):
    """ initializer called when used as a zope2 product """

    # setup non-anonymous file uploads
    import monkey
    monkey.__name__     # make pyflakes happy...

    # initialize portal content
    import content
    content.__name__    # make pyflakes happy...

    from Products.Archetypes import atapi
    from Products.CMFCore import utils

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(packageName), packageName)
    extra_constructors = {
        content.ATBlob: (content.addATBlobFile, content.addATBlobImage),
    }

    for atype, constructor in zip(content_types, constructors):
        extras = extra_constructors.get(atype, ())
        utils.ContentInit("%s: %s" % (packageName, atype.portal_type),
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,) + extras,
            ).initialize(context)


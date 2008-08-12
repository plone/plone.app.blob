from Testing.ZopeTestCase import app, close
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import PloneSite
from transaction import commit


class BlobLayer(PloneSite):
    """ layer for integration tests using blob types """

    @classmethod
    def setUp(cls):
        pass

    @classmethod
    def tearDown(cls):
        pass


class BlobReplacementLayer(PloneSite):
    """ layer for integration tests using replacement types """

    @classmethod
    def setUp(cls):
        root = app()
        portal = root.plone
        # import replacement profiles
        profile = 'profile-plone.app.blob:atfile-testing'
        tool = getToolByName(portal, 'portal_setup')
        tool.runAllImportStepsFromProfile(profile, purge_old=False)
        # make sure it's loaded...
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('File').product == 'plone.app.blob'
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass


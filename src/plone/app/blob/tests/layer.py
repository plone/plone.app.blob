from Testing.ZopeTestCase import app, close, installProduct
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase.layer import PloneSite
from transaction import commit


class BlobLayer(PloneSite):
    """ layer for integration tests using blob types """

    @classmethod
    def setUp(cls):
        # load zcml & install packages
        fiveconfigure.debug_mode = True
        from plone.app import blob
        zcml.load_config('configure.zcml', blob)
        from plone.app.blob import tests
        zcml.load_config('testing.zcml', tests)
        fiveconfigure.debug_mode = False
        # import the default profile
        root = app()
        portal = root.plone
        tool = getToolByName(portal, 'portal_setup')
        profile = 'profile-plone.app.blob:sample-type'
        tool.setImportContext(profile)
        tool.runAllImportSteps()
        # make sure it's loaded...
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass


class BlobFileReplacementLayer(BlobLayer):
    """ layer for integration tests using the file replacement type """

    @classmethod
    def setUp(cls):
        # load zcml & install packages
        fiveconfigure.debug_mode = True
        from plone.app import imaging
        zcml.load_config('configure.zcml', imaging)
        fiveconfigure.debug_mode = False
        # import replacement profiles
        root = app()
        portal = root.plone
        tool = getToolByName(portal, 'portal_setup')
        profile = 'profile-plone.app.blob:file-replacement'
        tool.setImportContext(profile)
        tool.runAllImportSteps()
        # make sure it's loaded...
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('File').product == 'plone.app.blob'
        # allow creating the replaced types
        types.getTypeInfo('ATFile').global_allow = True
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass


class BlobReplacementLayer(BlobLayer):
    """ layer for integration tests using replacement types """

    @classmethod
    def setUp(cls):
        # load zcml & install packages
        fiveconfigure.debug_mode = True
        from plone.app import imaging
        zcml.load_config('configure.zcml', imaging)
        fiveconfigure.debug_mode = False
        # import replacement profiles
        root = app()
        portal = root.plone
        tool = getToolByName(portal, 'portal_setup')
        for name in 'file-replacement', 'image-replacement':
            profile = 'profile-plone.app.blob:%s' % name
            tool.setImportContext(profile)
            tool.runAllImportSteps()
        tool.setImportContext('profile-plone.app.imaging:default')
        tool.runAllImportSteps()
        # make sure it's loaded...
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('File').product == 'plone.app.blob'
        # allow creating the replaced types
        types.getTypeInfo('ATFile').global_allow = True
        types.getTypeInfo('ATImage').global_allow = True
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass


class BlobLinguaLayer(PloneSite):
    """ layer for integration tests with LinguaPlone """

    @classmethod
    def setUp(cls):
        # load zcml
        fiveconfigure.debug_mode = True
        from Products import LinguaPlone
        zcml.load_config('configure.zcml', LinguaPlone)
        fiveconfigure.debug_mode = False
        # install package, import profile...
        installProduct('PloneLanguageTool', quiet=True)
        installProduct('LinguaPlone', quiet=True)
        root = app()
        portal = root.plone
        profile = 'profile-plone.app.blob:testing-lingua'
        tool = getToolByName(portal, 'portal_setup')
        tool.setImportContext(profile)
        tool.runAllImportSteps()
        qtool = getToolByName(portal, 'portal_quickinstaller')
        qtool.installProduct('LinguaPlone')
        # make sure it's loaded...
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('BlobelFish')
        # and commit the changes
        commit()
        close(root)

    @classmethod
    def tearDown(cls):
        pass

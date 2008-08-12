from plone.app.blob.tests import db # needs to be imported first to set up ZODB
db  # make pyflakes happy...

from Testing.ZopeTestCase import installPackage, app, close
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.CMFCore.utils import getToolByName
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import PloneSite, onsetup
from transaction import commit


@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import plone.app.blob
    zcml.load_config('configure.zcml', plone.app.blob)
    fiveconfigure.debug_mode = False
    installPackage('plone.app.blob')

setupPackage()
PloneTestCase.setupPloneSite(extension_profiles=(
    'plone.app.blob:default',
))


class BlobTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests """


class BlobFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ base class for functional tests """


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


class ReplacementTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


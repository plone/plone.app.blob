from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from plone.app.testing.bbb import PloneTestCaseFixture
from plone.app.testing.bbb import PTC_FIXTURE
from plone.testing import z2
from plone.app import testing
from plone.app.blob.tests.utils import getData


class BlobFixture(PloneTestCaseFixture):
    """ layer for integration tests using blob types """

    defaultBases = (PTC_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from plone.app.blob import tests
        self.loadZCML(package=tests, name="testing.zcml")
        z2.installProduct(app, 'plone.app.blob')

    def setUpPloneSite(self, portal):
        # install cmfeditions
        self.applyProfile(portal, 'plone.app.blob:sample-type')
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.blob')

BLOB_FIXTURE = BlobFixture()
BlobLayer = testing.FunctionalTesting(bases=(BLOB_FIXTURE, ), name="Blob:Functional")


class BlobReplacementFixture(PloneTestCaseFixture):
    """ layer for integration tests using replacement types """

    defaultBases = (BLOB_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from plone.app import imaging
        self.loadZCML(package=imaging)
        z2.installProduct(app, 'plone.app.imaging')

    def setUpPloneSite(self, portal):
        for name in ['file', 'image']:
            self.applyProfile(portal, 'plone.app.blob:%s-replacement' % name)
        # allow creating the replaced types
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'
        types.getTypeInfo('ATFile').global_allow = True
        types.getTypeInfo('ATImage').global_allow = True

        testing.setRoles(portal, testing.TEST_USER_ID, ['Manager'])
        folder = portal.portal_membership.getHomeFolder(testing.TEST_USER_ID)

        image = StringIO(getData('image.gif'))
        image.filename = 'original.gif'
        folder.invokeFactory('Image', id='foo-image', title='an image', image=image)

    def tearDownPloneSite(self, portal):
        folder = portal.portal_membership.getHomeFolder(testing.TEST_USER_ID)
        del folder['foo-image']

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.imaging')

BLOB_REPLACEMENT_FIXTURE = BlobReplacementFixture()
BlobReplacementLayer = testing.FunctionalTesting(
    bases=(BLOB_REPLACEMENT_FIXTURE, ), name="Blob Replacement:Functional")

# BBB
BlobFileReplacementLayer = BlobReplacementLayer


class BlobLinguaFixture(PloneTestCaseFixture):
    """ layer for integration tests with LinguaPlone """

    defaultBases = (PTC_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        from plone.app import imaging
        self.loadZCML(package=imaging)
        from plone.app.blob import tests
        self.loadZCML(name='testing.zcml', package=tests)
        from Products import LinguaPlone
        self.loadZCML(package=LinguaPlone)
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'Products.LinguaPlone')

    def setUpPloneSite(self, portal):
        profile = 'plone.app.blob:testing-lingua'
        self.applyProfile(portal, profile, purge_old=False)
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('BlobelFish')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.LinguaPlone')

BLOB_LINGUA_FIXTURE = BlobLinguaFixture()
BlobLinguaLayer = testing.FunctionalTesting(
    bases=(BLOB_LINGUA_FIXTURE, ), name="Blob Lingua:Functional")

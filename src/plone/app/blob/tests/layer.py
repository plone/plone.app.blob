from plone.app.testing.bbb import PloneTestCaseFixture
from plone.testing import z2
from plone.app import testing

from Products.CMFCore.utils import getToolByName


class BlobFixture(PloneTestCaseFixture):
    """ layer for integration tests using blob types """

    def setUpZope(self, app, configurationContext):
        super(BlobFixture, self).setUpZope(app, configurationContext)
        from plone.app.blob import tests
        self.loadZCML(package=tests, name="testing.zcml")
        z2.installProduct(app, 'plone.app.blob')

    def setUpPloneSite(self, portal):
        super(BlobFixture, self).setUpPloneSite(portal)
        # install cmfeditions
        testing.applyProfile(portal, 'profile-plone.app.blob:sample-type')
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'

    def tearDownZope(self, app):
        super(BlobFixture, self).tearDownZope(app)
        z2.uninstallProduct(app, 'plone.app.blob')


BLOB_FIXTURE = BlobFixture()
BlobLayer = testing.FunctionalTesting(bases=(BLOB_FIXTURE,), name="Blob:Functional")


class BlobFileReplacementFixture(PloneTestCaseFixture):
    """ layer for integration tests using the file replacement type """

    def setUpZope(self, app, configurationContext):
        super(BlobFileReplacementFixture, self).setUpZope(app, configurationContext)
        from plone.app import imaging
        self.loadZCML(package=imaging)
        z2.installProduct(app, 'plone.app.blob')

    def setUpPloneSite(self, portal):
        super(BlobFileReplacementFixture, self).setUpPloneSite(portal)
        # install cmfeditions
        testing.applyProfile(portal, 'profile-plone.app.blob:file-replacement',
                             purge_old=False)
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'
        types.getTypeInfo('ATFile').global_allow = True

    def tearDownZope(self, app):
        super(BlobFileReplacementFixture, self).tearDownZope(app)
        z2.uninstallProduct(app, 'plone.app.blob')


BLOB_FILE_REPLACEMENT_FIXTURE = BlobFileReplacementFixture()
BlobFileReplacementLayer = testing.FunctionalTesting(
    bases=(BLOB_FILE_REPLACEMENT_FIXTURE,), name="Blob File Replacement:Functional")


class BlobReplacementFixture(PloneTestCaseFixture):
    """ layer for integration tests using replacement types """

    def setUpZope(self, app, configurationContext):
        super(BlobReplacementFixture, self).setUpZope(app, configurationContext)
        from plone.app import imaging
        self.loadZCML(package=imaging)
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'plone.app.imaging')

    def setUpPloneSite(self, portal):
        super(BlobReplacementFixture, self).setUpPloneSite(portal)
        for name in 'file-replacement', 'image-replacement':
            profile = 'profile-plone.app.blob:%s' % name
            testing.applyProfile(portal, profile, purge_old=False)
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('Blob').product == 'plone.app.blob'
        types.getTypeInfo('ATFile').global_allow = True
        types.getTypeInfo('ATImage').global_allow = True

    def tearDownZope(self, app):
        super(BlobReplacementFixture, self).tearDownZope(app)
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'plone.app.imaging')


BLOB_REPLACEMENT_FIXTURE = BlobReplacementFixture()
BlobReplacementLayer = testing.FunctionalTesting(
    bases=(BLOB_REPLACEMENT_FIXTURE,), name="Blob Replacement:Functional")


class BlobLinguaFixture(PloneTestCaseFixture):
    """ layer for integration tests with LinguaPlone """

    def setUpZope(self, app, configurationContext):
        super(BlobLinguaFixture, self).setUpZope(app, configurationContext)
        from plone.app import imaging
        self.loadZCML(package=imaging)
        from plone.app.blob import tests
        self.loadZCML(name='testing.zcml', package=tests)
        from Products import LinguaPlone
        self.loadZCML(package=LinguaPlone)
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'Products.LinguaPlone')

    def setUpPloneSite(self, portal):
        super(BlobLinguaFixture, self).setUpPloneSite(portal)
        profile = 'profile-plone.app.blob:testing-lingua'
        self.applyProfile(profile, purge_old=False)
        types = getToolByName(portal, 'portal_types')
        assert types.getTypeInfo('BlobelFish')

    def tearDownZope(self, app):
        super(BlobLinguaFixture, self).tearDownZope(app)
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.LinguaPlone')


BLOB_LINGUA_FIXTURE = BlobLinguaFixture()
BlobLinguaLayer = testing.FunctionalTesting(
    bases=(BLOB_LINGUA_FIXTURE,), name="Blob Lingua:Functional")

from Testing.ZopeTestCase import installPackage, Sandboxed
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer
from plone.app.blob.tests.layer import BlobLinguaLayer

try:
    # try to import the sample type for testing LinguaPlone
    from plone.app.blob.tests import lingua
    lingua      # make pyflakes happy
except ImportError:
    pass

@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import plone.app.blob
    zcml.load_config('configure.zcml', plone.app.blob)
    import plone.app.imaging
    zcml.load_config('configure.zcml', plone.app.imaging)
    fiveconfigure.debug_mode = False
    installPackage('plone.app.blob', quiet=True)
    installPackage('plone.app.imaging', quiet=True)

setupPackage()
PloneTestCase.setupPloneSite(extension_profiles=(
    'plone.app.blob:sample-type',
    'plone.app.imaging:default',
))


class BlobTestCase(Sandboxed, PloneTestCase.PloneTestCase):
    """ base class for integration tests """

    layer = BlobLayer


class BlobFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ base class for functional tests """

    layer = BlobLayer

    def getCredentials(self):
        return '%s:%s' % (PloneTestCase.default_user,
            PloneTestCase.default_password)

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            auth = 'Basic %s' % self.getCredentials()
            browser.addHeader('Authorization', auth)
        return browser


class ReplacementTestCase(Sandboxed, PloneTestCase.PloneTestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


class ReplacementFunctionalTestCase(BlobFunctionalTestCase):
    """ base class for functional tests """

    layer = BlobReplacementLayer


class BlobLinguaTestCase(BlobTestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


class BlobLinguaFunctionalTestCase(BlobFunctionalTestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


from Testing.ZopeTestCase import Sandboxed
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer
from plone.app.blob.tests.layer import BlobLinguaLayer

try:
    # try to import the sample type for testing LinguaPlone
    from plone.app.blob.tests import lingua
    lingua      # make pyflakes happy
except ImportError:
    pass


PloneTestCase.setupPloneSite()


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

import unittest
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer
from plone.app.blob.tests.layer import BlobLinguaLayer
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD

from plone.testing.z2 import Browser


class BlobTestCase(unittest.TestCase):
    """ base class for integration tests """

    layer = BlobLayer


class BlobFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLayer


class ReplacementTestCase(unittest.TestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer

    def getCredentials(self):
        return '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.layer['app'])
        if loggedIn:
            auth = 'Basic %s' % self.getCredentials()
            browser.addHeader('Authorization', auth)
        return browser


class ReplacementFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobReplacementLayer


class BlobLinguaTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


class BlobLinguaFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer

from plone.app.blob.tests import db # needs to be imported first to set up ZODB
db  # make pyflakes happy...

from Testing.ZopeTestCase import installPackage
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer


@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import plone.app.blob
    zcml.load_config('configure.zcml', plone.app.blob)
    import plone.app.imaging
    zcml.load_config('configure.zcml', plone.app.imaging)
    fiveconfigure.debug_mode = False
    installPackage('plone.app.blob')

setupPackage()
PloneTestCase.setupPloneSite(extension_profiles=(
    'plone.app.blob:default',
    'plone.app.imaging:default',
))


class BlobTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests """

    layer = BlobLayer


class BlobFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ base class for functional tests """

    layer = BlobLayer

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = PloneTestCase.default_user
            pwd = PloneTestCase.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser


class ReplacementTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


class ReplacementFunctionalTestCase(BlobFunctionalTestCase):
    """ base class for functional tests """

    layer = BlobReplacementLayer


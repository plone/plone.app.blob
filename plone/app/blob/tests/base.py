from plone.app.blob.tests import db # needs to be imported first to set up ZODB
db  # make pyflakes happy...

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer


@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import plone.app.blob
    zcml.load_config('configure.zcml', plone.app.blob)
    fiveconfigure.debug_mode = False

    # make sure the monkey patches from `pythonproducts` are appied; they get
    # loaded with an `installProduct('Five')`, but zcml layer's `setUp()`
    # calls `five.safe_load_site()`, which in turn calls `cleanUp()` from
    # `zope.testing.cleanup`, effectively removing the patches again *before*
    # the tests are run; so we need to explicitly apply them again... %)
    from Products.Five import pythonproducts
    pythonproducts.applyPatches()
     

setupPackage()
PloneTestCase.setupPloneSite(extension_profiles=(
    'plone.app.blob:default',
))


class BlobTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests """

    layer = BlobLayer


class BlobFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ base class for functional tests """

    layer = BlobLayer


class ReplacementTestCase(PloneTestCase.PloneTestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


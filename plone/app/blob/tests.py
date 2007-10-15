from unittest import TestSuite
from Testing.ZopeTestCase import installPackage, ZopeDocFileSuite
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup


@onsetup
def setupPackage():
    """ set up the package and its dependencies """
    fiveconfigure.debug_mode = True
    import plone.app.blob
    zcml.load_config('configure.zcml', plone.app.blob)
    fiveconfigure.debug_mode = False
    installPackage('plone.app.blob')

setupPackage()
PloneTestCase.setupPloneSite(products=(
    'plone.app.blob',
))


def test_suite():
    return TestSuite((
        ZopeDocFileSuite(
           'README.txt', package='plone.app.blob',
           test_class=PloneTestCase.FunctionalTestCase),
    ))


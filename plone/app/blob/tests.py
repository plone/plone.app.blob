from plone.app.blob import db   # needs to be imported first to set up ZODB

from unittest import TestSuite, makeSuite
from Testing.ZopeTestCase import installPackage, ZopeDocFileSuite
from ZPublisher.HTTPRequest import HTTPRequest
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

from plone.app.blob.utils import guessMimetype

from StringIO import StringIO
from base64 import decodestring


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


test_environment = {
    'CONTENT_TYPE': 'multipart/form-data; boundary=12345',
    'REQUEST_METHOD': 'POST',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '80',
}

largefile_data = '''
--12345
Content-Disposition: form-data; name="file"; filename="file"
Content-Type: application/octet-stream

test %s

''' % ('test' * 1000)


class BlobTestCase(PloneTestCase.PloneTestCase):

    def testFileName(self):
        """ checks fileupload object supports the filename """
        req = HTTPRequest(StringIO(largefile_data), test_environment.copy(), None)
        req.processInputs()
        f = req.form.get('file')
        self.assert_(f.name)

    def testMimetypeGuessing(self):
        gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
        gif = StringIO(decodestring(gif))
        self.assertEqual(guessMimetype(gif), 'image/gif')
        self.assertEqual(guessMimetype(gif, 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO(), 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO('foo')), 'text/plain')


def test_suite():
    return TestSuite((
        makeSuite(BlobTestCase),
        ZopeDocFileSuite(
           'README.txt', package='plone.app.blob',
           test_class=PloneTestCase.FunctionalTestCase),
    ))


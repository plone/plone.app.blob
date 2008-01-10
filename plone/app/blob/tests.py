from plone.app.blob import db   # needs to be imported first to set up ZODB

from unittest import TestSuite, makeSuite
from Testing.ZopeTestCase import ZopeDocFileSuite
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

    gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
    pdf = '%PDF-1.4 fake pdf...'

    def testFileName(self):
        """ checks fileupload object supports the filename """
        req = HTTPRequest(StringIO(largefile_data), test_environment.copy(), None)
        req.processInputs()
        f = req.form.get('file')
        self.assert_(f.name)

    def testMimetypeGuessing(self):
        def guessMimetype(data, filename):
            guessMimetype(data, filename, context=self.portal)
        gif = StringIO(decodestring(self.gif))
        self.assertEqual(guessMimetype(gif), 'image/gif')
        self.assertEqual(guessMimetype(gif, 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO(), 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO('foo')), 'text/plain')

    def testStringValue(self):
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        value = decodestring(self.gif)
        blob.update(title="I'm blob", file=value)
        self.assertEqual(blob.getContentType(), 'image/gif')
        self.assertEqual(str(blob.getFile()), value)
        blob.update(title="I'm blob", file='plain text')
        self.assertEqual(blob.getContentType(), 'text/plain')
        self.assertEqual(str(blob.getFile()), 'plain text')
        blob.update(title="I'm blob", file='')
        self.assertEqual(blob.getContentType(), 'text/plain')
        self.assertEqual(str(blob.getFile()), '')

    def testIcon(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo')
        blob = self.folder.blob
        blob.update(file=decodestring(self.gif))
        self.assertEqual(blob.getIcon(), 'plone/image.png')
        blob.update(file=self.pdf)
        self.assertEqual(blob.getIcon(), 'plone/pdf.png')
        blob.update(file='some text...')
        self.assertEqual(blob.getIcon(), 'plone/txt.png')


def test_suite():
    return TestSuite((
        makeSuite(BlobTestCase),
        ZopeDocFileSuite(
           'README.txt', package='plone.app.blob',
           test_class=PloneTestCase.FunctionalTestCase),
    ))


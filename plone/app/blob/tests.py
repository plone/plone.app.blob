from plone.app.blob import db   # needs to be imported first to set up ZODB

import os.path
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

largefile_data = ('test' * 2048)

upload_request = '''
--12345
Content-Disposition: form-data; name="file"; filename="%s"
Content-Type: application/octet-stream
Content-Length: %d

%s

'''

def makeFileUpload(data, filename):
    request_data = upload_request % (filename, len(data), data)
    req = HTTPRequest(StringIO(request_data),
                      test_environment.copy(),
                      None)
    req.processInputs()
    return req.form.get('file')

class BlobTestCase(PloneTestCase.PloneTestCase):

    gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
    pdf = '%PDF-1.4 fake pdf...'

    def testFileName(self):
        """ checks fileupload object supports the filename """
        f = makeFileUpload(largefile_data, 'test.txt')
        self.assert_(os.path.isfile(f.name))

    def testMimetypeGuessing(self):
        gif = StringIO(decodestring(self.gif))
        self.assertEqual(guessMimetype(gif), 'image/gif')
        self.assertEqual(guessMimetype(gif, 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO(), 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO('foo')), 'text/plain')

    def testFileUploadPatch(self):
        f = makeFileUpload(largefile_data, 'test.txt')
        name = f.name
        # the filesystem file of a large file should exist
        self.failUnless(os.path.isfile(name), name)
        # even after it's been closed
        f.close()
        self.failUnless(os.path.isfile(name), name)
        # but should go away when deleted
        del f
        self.failIf(os.path.isfile(name), name)

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

    def testSize(self):
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        # test with a small file
        gif = decodestring(self.gif)
        f = makeFileUpload(gif, 'test.gif')
        blob.update(file=f)
        self.assertEqual(blob.get_size(), len(gif))
        # and a large one
        f = makeFileUpload(largefile_data, 'test.txt')
        blob.update(file=f)
        self.assertEqual(blob.get_size(), len(largefile_data))

    def testOpenAfterConsume(self):
        """it's an expected use case to be able to open a blob for reading
        immediately after populating it by consuming"""
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        f = makeFileUpload(largefile_data, 'test.txt')
        blob.update(file=f)
        b = blob.getFile().getBlob().open('r')
        self.assertEqual(b.read(10), largefile_data[:10])
        b.close()
        import transaction
        transaction.savepoint()

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


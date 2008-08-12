from plone.app.blob.tests.base import BlobTestCase      # import first!

import os.path
from unittest import defaultTestLoader

from plone.app.blob.utils import guessMimetype
from plone.app.blob.tests.utils import makeFileUpload

from StringIO import StringIO
from base64 import decodestring


largefile_data = ('test' * 2048)


class IntegrationTests(BlobTestCase):

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
        blob.update(file=makeFileUpload(gif, 'test.gif'))
        self.assertEqual(blob.get_size(), len(gif))
        # and a large one
        blob.update(file=makeFileUpload(largefile_data, 'test.txt'))
        self.assertEqual(blob.get_size(), len(largefile_data))

    def testOpenAfterConsume(self):
        """ it's an expected use case to be able to open a blob for
            reading immediately after populating it by consuming """
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        blob.update(file=makeFileUpload(largefile_data, 'test.txt'))
        b = blob.getFile().getBlob().open('r')
        self.assertEqual(b.read(10), largefile_data[:10])

    def testIcon(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo')
        blob = self.folder.blob
        blob.update(file=decodestring(self.gif))
        self.assertEqual(blob.getIcon(), 'plone/image.png')
        blob.update(file=self.pdf)
        self.assertEqual(blob.getIcon(), 'plone/pdf.png')
        blob.update(file='some text...')
        self.assertEqual(blob.getIcon(), 'plone/txt.png')

    def testIconLookupForUnknownMimeType(self):
        """ test for http://plone.org/products/plone.app.blob/issues/1 """
        self.folder.invokeFactory('File', 'foo', file='foo')
        self.folder.foo.setContentType('application/foo')
        self.folder.invokeFactory('Blob', 'blob')
        self.folder.blob.update(file=self.folder.foo)
        self.assertEqual(self.folder.blob.getIcon(), 'plone/file_icon.gif')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)


from plone.app.blob.tests.base import BlobTestCase      # import first!

from unittest import defaultTestLoader
from plone.app.blob.utils import guessMimetype
from plone.app.blob.tests.utils import makeFileUpload, getImage
from StringIO import StringIO
from os.path import isfile


largefile_data = ('test' * 2048)
pdf_data = '%PDF-1.4 fake pdf...'


class IntegrationTests(BlobTestCase):

    def testFileName(self):
        """ checks fileupload object supports the filename """
        f = makeFileUpload(largefile_data, 'test.txt')
        self.assert_(isfile(f.name))

    def testMimetypeGuessing(self):
        gif = StringIO(getImage())
        self.assertEqual(guessMimetype(gif), 'image/gif')
        self.assertEqual(guessMimetype(gif, 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO(), 'image.jpg'), 'image/jpeg')
        self.assertEqual(guessMimetype(StringIO('foo')), 'text/plain')

    def testFileUploadPatch(self):
        f = makeFileUpload(largefile_data, 'test.txt')
        name = f.name
        # the filesystem file of a large file should exist
        self.failUnless(isfile(name), name)
        # even after it's been closed
        f.close()
        self.failUnless(isfile(name), name)
        # but should go away when deleted
        del f
        self.failIf(isfile(name), name)

    def testStringValue(self):
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        value = getImage()
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
        gif = getImage()
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
        blob.update(file=getImage())
        self.assertEqual(blob.getIcon(), 'plone/image.png')
        blob.update(file=pdf_data)
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


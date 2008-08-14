from plone.app.blob.tests.base import ReplacementTestCase   # import first!

from unittest import defaultTestLoader
from Products.ATContentTypes.interface.file import IATFile, IFileContent
from plone.app.blob.interfaces import IATBlobFile
from plone.app.blob.field import BlobField
from plone.app.blob.content import ATBlob


class FileReplacementTests(ReplacementTestCase):

    def testCreateFileBlob(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        foo.update(title="I'm blob", file='plain text')
        # check content item
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(str(foo.getFile()), 'plain text')
        # also make sure we're using blobs
        self.failUnless(isinstance(foo, ATBlob), 'no atblob?')
        self.failUnless(isinstance(foo.getField('file'), BlobField), 'no blob?')
        blob = foo.getFile().getBlob().open('r')
        self.assertEqual(blob.read(), 'plain text')

    def testFileBlobInterfaces(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        self.failUnless(IATFile.providedBy(foo), 'no IATFile?')
        self.failUnless(IFileContent.providedBy(foo), 'no IFileContent?')
        self.failUnless(IATBlobFile.providedBy(foo), 'no IATBlobFile?')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)


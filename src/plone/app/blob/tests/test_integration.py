from unittest import TestSuite, makeSuite
from plone.app.blob.tests.base import BlobTestCase, BlobFunctionalTestCase

from plone.app.blob.utils import guessMimetype
from plone.app.blob.tests.utils import makeFileUpload, getImage, getData
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

    def testGetSizeOnFileContent(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo', file=pdf_data)
        blob = self.folder['blob']
        field = blob.getFile()
        self.assertRaises(AttributeError, field.getSize)

    def testZeroLengthNamedFileIsBooleanTrue(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo', file='')
        blob = self.folder['blob'].getFile()
        self.assertEqual(len(blob), 0)
        self.failIf(bool(blob))
        blob.setFilename('foo.txt')
        self.failUnless(bool(blob))

    def testAbsoluteURL(self):
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        url = self.folder.absolute_url() + '/blob'
        self.assertEqual(blob.absolute_url(), url)
        self.assertEqual(blob.getFile().absolute_url(), url)

    def testIndexAccessor(self):
        blob = self.folder[self.folder.invokeFactory('Blob', 'blob',
            title='foo', file=getData('plone.pdf'))]
        field = blob.getField('file')
        accessor = field.getIndexAccessor(blob)
        self.assertEqual(field.index_method, accessor.func_name)
        data = accessor()
        self.failUnless('Plone' in data, 'pdftohtml not installed?')
        self.failIf('PDF' in data)

    def testSearchableText(self):
        blob = self.folder[self.folder.invokeFactory('Blob', 'blob',
            title='foo', file=getData('plone.pdf'))]
        data = blob.SearchableText()
        self.failUnless('blob' in data)
        self.failUnless('foo' in data)
        self.failUnless('Plone' in data, 'pdftohtml not installed?')
        self.failIf('PDF' in data)

    def testOpenAfterConsume(self):
        """ it's an expected use case to be able to open a blob for
            reading immediately after populating it by consuming """
        self.folder.invokeFactory('Blob', 'blob')
        blob = self.folder['blob']
        blob.update(file=makeFileUpload(largefile_data, 'test.txt'))
        b = blob.getFile().getBlob().open('r')
        self.assertEqual(b.read(10), largefile_data[:10])

    def testRangeSupport(self):
        blob = self.folder[self.folder.invokeFactory('Blob', 'blob',
            title='foo', file=getData('plone.pdf'))]
        data = blob.getFile().getBlob().open('r').read()
        request = self.folder.REQUEST
        request.environ['HTTP_RANGE'] = 'bytes=2-10'
        iterator = blob.download(request)
        self.assertEqual(data[2:10+1], iterator.next())
        # ranges should also work with multiple chunks read from the blob
        request.environ['HTTP_RANGE'] = 'bytes=2-10'
        iterator = blob.download(request)
        iterator.streamsize = 5
        self.assertEqual(data[2:2+5], iterator.next())
        self.assertEqual(data[2+5:10+1], iterator.next())
        # open and suffix ranges also have to work
        request.environ['HTTP_RANGE'] = 'bytes=2-'
        iterator = blob.download(request)
        self.assertEqual(data[2:], ''.join(iterator))
        request.environ['HTTP_RANGE'] = 'bytes=-20'
        iterator = blob.download(request)
        self.assertEqual(data[-20:], ''.join(iterator))

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
        self.folder.invokeFactory('Blob', 'blob', file='foo')
        self.folder.blob.getFile().setContentType('application/foo')
        self.failUnless(self.folder.blob.getIcon().endswith('file_icon.gif'))

    def testVersioning(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo')
        blob = self.folder.blob
        blob.edit(file=pdf_data)
        repository = self.portal.portal_repository
        repository.applyVersionControl(blob, comment='version 1')
        blob.edit(file='some text...')
        repository.save(blob, comment='version 2')

        # blob-based file/image content isn't versionable yet, so the
        # remaining tests are skipped for the time being...
        # note: the `revert` needs to stay or else `tearDown` will break
        #   with "ConnectionStateError: Cannot close a connection joined
        #   to a transaction"

        version = repository.retrieve(blob, 0)
        version.object.data     # trigger opening of blob...
        # self.assertEqual(version.object.data, pdf_data)
        # version = repository.retrieve(blob, 1)
        # self.assertEqual(version.object.data, 'some text...')
        repository.revert(blob, 0)
        # self.assertEqual(blob.data, pdf_data)

    def testTitleNotRequired(self):
        self.folder.invokeFactory('Blob', 'blob', title='foo')
        blob = self.folder.blob
        self.failIf(blob.Schema()['title'].required)


class FunctionalIntegrationTests(BlobFunctionalTestCase):

    def testDefaultView(self):
        self.folder.invokeFactory('Blob', 'blob', title='Foo Bar', file=pdf_data)
        base = '/'.join(self.folder.blob.getPhysicalPath())
        credentials = self.getCredentials()
        output = str(self.publish(base + '/view', basic=credentials))
        self.failUnless('Foo Bar' in output, '404?')
        self.failUnless('PDF document' in output, '404?')
        self.failIf("We're sorry, but that page doesn't exist" in output, '404!')

    def testInlineMimetypes(self):
        obj = self.folder[self.folder.invokeFactory('Blob', 'blob')]
        def disposition(mimetype, filename):
            obj.setFormat(mimetype)
            obj.setFilename(filename)
            response = self.publish('/%s' % obj.absolute_url(relative=True),
                basic=self.getCredentials())
            self.assertEqual(response.getStatus(), 200)
            return response.getHeader('Content-Disposition')
        # only PDFs and Office files are shown inline
        self.assertEqual(disposition('application/pdf', 'foo.pdf'),
            'inline; filename="foo.pdf"')
        self.assertEqual(disposition('application/msword', 'foo.doc'),
            'inline; filename="foo.doc"')
        self.assertEqual(disposition('application/x-msexcel', 'foo.xls'),
            'inline; filename="foo.xls"')
        self.assertEqual(disposition('text/plain', 'foo.txt'),
            'attachment; filename="foo.txt"')
        self.assertEqual(disposition('application/octet-stream', 'foo.exe'),
            'attachment; filename="foo.exe"')


def test_suite():
    return TestSuite([
        makeSuite(IntegrationTests),
        makeSuite(FunctionalIntegrationTests),
    ])

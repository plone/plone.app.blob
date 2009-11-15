from StringIO import StringIO

from plone.app.blob.tests.base import ReplacementTestCase   # import first!

from unittest import defaultTestLoader
from zope.interface.interfaces import IInterface
from Products.ATContentTypes.interface import file as atfile
from Products.ATContentTypes.interface import image as atimage
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
from plone.app.blob.interfaces import IATBlobFile, IATBlobImage
from plone.app.blob.migrations import migrateATBlobFiles, migrateATBlobImages
from plone.app.blob.field import BlobField
from plone.app.blob.content import ATBlob
from plone.app.blob.tests.utils import getImage, getData


def permissionsFor(name, product):
    from Products import meta_types
    for mt in meta_types:
        if mt['product'] == product and name in mt['name']:
            yield mt['permission']


class FileReplacementTests(ReplacementTestCase):

    def testAddFilePermission(self):
        permissions = list(permissionsFor('File', 'plone.app.blob'))
        self.assertEqual(permissions, ['ATContentTypes: Add File'])

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
        # let's also check the `get_size` and `index_html` methods, the
        # latter of which should return a stream-iterator
        self.assertEqual(foo.get_size(), 10)
        request = foo.REQUEST
        response = request.RESPONSE
        orig_out = request.response.stdout
        out = request.response.stdout = StringIO()
        try:
            foo.index_html(request, response)
        finally:
            request.response.stdout = orig_out

        header_len = 192
        self.assertEqual(out.getvalue()[header_len:], 'plain text')
        headers = response.headers
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.headers['content-length'], '10')
        self.assertEqual(response.headers['content-type'], 'text/plain')

    def testFileBlobInterfaces(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        self.failUnless(atfile.IATFile.providedBy(foo), 'no IATFile?')
        self.failUnless(atfile.IFileContent.providedBy(foo), 'no IFileContent?')
        self.failUnless(IATBlobFile.providedBy(foo), 'no IATBlobFile?')
        if not IInterface.providedBy(Z2IATFile):    # this is zope < 2.12
            self.failUnless(Z2IATFile.isImplementedBy(foo), 'no zope2 IATFile?')
            self.failIf(Z2IATImage.isImplementedBy(foo), 'zope2 IATImage?')

    def testFileMigration(self):
        foo = self.folder[self.folder.invokeFactory('ATFile', id='foo',
            title='a file', file='plain text', subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('File')
        foo.reindexObject(idxs=('portal_type',))
        # check to be migrated content
        self.failUnless(isinstance(foo, ATFile), 'not a file?')
        self.assertEqual(foo.Title(), 'a file')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobFiles(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (File -> File)\n')
        foo = self.folder['foo']
        self.failUnless(isinstance(foo, ATBlob), 'not a blob?')
        self.failUnless(isinstance(foo.getField('file'), BlobField), 'no blob?')
        self.assertEqual(foo.Title(), 'a file')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), 'plain text')

    def testCatalogAfterFileMigration(self):
        foo = self.folder[self.folder.invokeFactory('ATFile', id='foo',
            title='a file', file='plain text', subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('File')
        foo.reindexObject(idxs=('portal_type',))
        # remember the catalog data so it can be checked
        catalog = self.portal.portal_catalog
        rid = catalog(id='foo')[0].getRID()
        index_data = catalog.getIndexDataForRID(rid)
        meta_data = catalog.getMetadataForRID(rid)
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobFiles(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (File -> File)\n')
        foo = self.folder['foo']
        brain = catalog(id='foo')[0]
        self.assertEqual(foo.UID(), brain.UID)
        self.assertEqual(foo.getObjSize(), brain.getObjSize)
        self.assertEqual(foo.getPortalTypeName(), brain.Type)
        # compare pre-migration and current catalog data...
        okay = ('meta_type', 'Type', 'object_provides', 'SearchableText', 'Language')
        for key, value in catalog.getIndexDataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(index_data[key], value, 'index: %s' % key)
        okay = ('meta_type',)
        for key, value in catalog.getMetadataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(meta_data[key], value, 'meta: %s' % key)

    def testIndexAccessor(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        field = foo.getField('file')
        accessor = field.getIndexAccessor(foo)
        self.assertEqual(field.index_method, accessor.func_name)
        data = accessor()
        self.failUnless('Plone' in data, 'pdftohtml not installed?')
        self.failIf('PDF' in data)

    def testSearchableText(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        data = foo.SearchableText()
        self.failUnless('foo' in data)
        self.failUnless('Plone' in data, 'pdftohtml not installed?')
        self.failIf('PDF' in data)


class ImageReplacementTests(ReplacementTestCase):

    def testAddImagePermission(self):
        permissions = list(permissionsFor('Image', 'plone.app.blob'))
        self.assertEqual(permissions, ['ATContentTypes: Add Image'])

    def testCreateImageBlob(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('Image', 'foo')]
        foo.update(title="I'm blob", image=gif)
        # check content item
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(str(foo.getImage()), gif)
        # also make sure we're using blobs
        self.failUnless(isinstance(foo, ATBlob), 'no atblob?')
        self.failUnless(isinstance(foo.getField('image'), BlobField), 'no blob?')
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), gif)
        # let's also check the `getSize`, `tag` and `index_html` methods
        # as well as the size attributes
        self.assertEqual(foo.getSize(), (1, 1))
        self.assertEqual(foo.width, 1)
        self.assertEqual(foo.height, 1)
        self.failUnless('/foo/image"' in foo.tag())
        # `index_html` should return a stream-iterator
        request = foo.REQUEST
        response = request.RESPONSE
        orig_out = request.response.stdout
        out = request.response.stdout = StringIO()
        try:
            foo.index_html(request, response)
        finally:
            request.response.stdout = orig_out

        header_len = 191
        self.assertEqual(out.getvalue()[header_len:], gif)
        headers = response.headers
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.headers['content-length'], '43')
        self.assertEqual(response.headers['content-type'], 'image/gif')

    def testImageBlobInterfaces(self):
        foo = self.folder[self.folder.invokeFactory('Image', 'foo')]
        self.failUnless(atimage.IATImage.providedBy(foo), 'no IATImage?')
        self.failUnless(atimage.IImageContent.providedBy(foo), 'no IImageContent?')
        self.failUnless(IATBlobImage.providedBy(foo), 'no IATBlobImage?')
        if not IInterface.providedBy(Z2IATFile):    # this is zope < 2.12
            self.failUnless(Z2IATImage.isImplementedBy(foo), 'no zope2 IATImage?')
            self.failIf(Z2IATFile.isImplementedBy(foo), 'zope2 IATFile?')

    def testImageMigration(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('ATImage', id='foo',
            title='an image', image=gif, subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('Image')
        foo.reindexObject(idxs=('portal_type',))
        # check to be migrated content
        self.failUnless(isinstance(foo, ATImage), 'not an image?')
        self.assertEqual(foo.Title(), 'an image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobImages(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (Image -> Image)\n')
        foo = self.folder['foo']
        self.failUnless(isinstance(foo, ATBlob), 'not a blob?')
        self.failUnless(isinstance(foo.getField('image'), BlobField), 'no blob?')
        self.assertEqual(foo.Title(), 'an image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me',))
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), gif)

    def testCatalogAfterImageMigration(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('ATImage', id='foo',
            title='an image', image=gif, subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('Image')
        foo.reindexObject(idxs=('portal_type',))
        # remember the catalog data so it can be checked
        catalog = self.portal.portal_catalog
        rid = catalog(id='foo')[0].getRID()
        index_data = catalog.getIndexDataForRID(rid)
        meta_data = catalog.getMetadataForRID(rid)
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobImages(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (Image -> Image)\n')
        foo = self.folder['foo']
        brain = catalog(id='foo')[0]
        self.assertEqual(foo.UID(), brain.UID)
        self.assertEqual(foo.getObjSize(), brain.getObjSize)
        self.assertEqual(foo.getPortalTypeName(), brain.Type)
        # compare pre-migration and current catalog data...
        okay = ('meta_type', 'Type', 'object_provides', 'Language')
        for key, value in catalog.getIndexDataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(index_data[key], value, 'index: %s' % key)
        okay = ('meta_type', 'getIcon')
        for key, value in catalog.getMetadataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(meta_data[key], value, 'meta: %s' % key)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)


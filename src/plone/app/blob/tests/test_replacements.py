from plone.app.blob.tests.base import ReplacementTestCase   # import first!

from unittest import defaultTestLoader
from zope.interface.interfaces import IInterface
from zope.annotation import IAnnotations
from Products.Archetypes.atapi import ImageField, AnnotationStorage
from Products.Archetypes.Field import Image
from Products.ATContentTypes.interface import file as atfile
from Products.ATContentTypes.interface import image as atimage
from Products.ATContentTypes.interfaces import IATFile as Z2IATFile
from Products.ATContentTypes.interfaces import IATImage as Z2IATImage
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
from Products.GenericSetup.interfaces import IFilesystemExporter, \
    IFilesystemImporter
from plone.app.blob.interfaces import IATBlobFile, IATBlobImage
from plone.app.blob.migrations import migrate
from plone.app.blob.migrations import migrateATBlobFiles, migrateATBlobImages
from plone.app.blob.field import BlobField
from plone.app.blob.content import ATBlob
from plone.app.blob.tests.utils import getImage, getData
from ZODB.blob import SAVEPOINT_SUFFIX
from plone.app.blob.tests.base import changeAllowedSizes


def permissionsFor(name, product):
    from Products import meta_types
    for mt in meta_types:
        if mt['product'] == product and name in mt['name']:
            yield mt['permission']


class FileReplacementTests(ReplacementTestCase):

    def testAddFilePermission(self):
        permissions = permissionsFor('File', 'plone.app.blob')
        self.assertTrue('ATContentTypes: Add File' in permissions)

    def testCreateFileBlob(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        foo.update(title="I'm blob", file='plain text')
        # check content item
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(str(foo.getFile()), 'plain text')
        # also make sure we're using blobs
        self.assertTrue(isinstance(foo, ATBlob), 'no atblob?')
        self.assertTrue(isinstance(foo.getField('file'), BlobField), 'no blob?')
        blob = foo.getFile().getBlob().open('r')
        self.assertEqual(blob.read(), 'plain text')
        # let's also check the `get_size` and `index_html` methods, the
        # latter of which should return a stream-iterator
        self.assertEqual(foo.get_size(), 10)
        request = foo.REQUEST
        response = request.RESPONSE
        self.assertEqual(foo.index_html(request, response).next(), 'plain text')
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.headers['content-length'], '10')
        self.assertEqual(response.headers['content-type'], 'text/plain')

    def testFileBlobInterfaces(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        self.assertTrue(atfile.IATFile.providedBy(foo), 'no IATFile?')
        self.assertTrue(atfile.IFileContent.providedBy(foo), 'no IFileContent?')
        self.assertTrue(IATBlobFile.providedBy(foo), 'no IATBlobFile?')
        if not IInterface.providedBy(Z2IATFile):    # this is zope < 2.12
            self.assertTrue(Z2IATFile.isImplementedBy(foo), 'no zope2 IATFile?')
            self.assertFalse(Z2IATImage.isImplementedBy(foo), 'zope2 IATImage?')

    def testFileMigration(self):
        foo = self.folder[self.folder.invokeFactory('ATFile', id='foo',
            title='a file', file='plain text', subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('File')
        foo.reindexObject(idxs=('portal_type', ))
        # check to be migrated content
        self.assertTrue(isinstance(foo, ATFile), 'not a file?')
        self.assertEqual(foo.Title(), 'a file')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me', ))
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobFiles(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (File -> File)\n')
        foo = self.folder['foo']
        self.assertTrue(isinstance(foo, ATBlob), 'not a blob?')
        self.assertTrue(isinstance(foo.getField('file'), BlobField), 'no blob?')
        self.assertEqual(foo.Title(), 'a file')
        self.assertEqual(foo.getContentType(), 'text/plain')
        self.assertEqual(foo.getPortalTypeName(), 'File')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me', ))
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), 'plain text')

    def testCatalogAfterFileMigration(self):
        foo = self.folder[self.folder.invokeFactory('ATFile', id='foo',
            title='a file', file='plain text', subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('File')
        foo.reindexObject(idxs=('portal_type', ))
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
        okay = ('meta_type', )
        for key, value in catalog.getMetadataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(meta_data[key], value, 'meta: %s' % key)
        # also make sure the `Type` index has been updated correctly
        brains = catalog(Type='File')
        self.assertEqual([b.getObject() for b in brains], [foo])

    def testIndexAccessor(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        field = foo.getField('file')
        accessor = field.getIndexAccessor(foo)
        self.assertEqual(field.index_method, accessor.func_name)
        data = accessor()
        self.assertTrue('Plone' in data, 'pdftohtml not installed?')
        self.assertFalse('PDF' in data)

    def testSearchableText(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        data = foo.SearchableText()
        self.assertTrue('foo' in data)
        self.assertTrue('Plone' in data, 'pdftohtml not installed?')
        self.assertFalse('PDF' in data)

    def testBlobPath(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        field = foo.getField('file')
        blobfile = field.get(foo).blob._p_blob_committed
        tempdir = self.app._p_jar._storage.temporaryDirectory()
        self.assertTrue(blobfile.endswith(SAVEPOINT_SUFFIX))
        self.assertTrue(blobfile.startswith(tempdir))

    def testGSContentCompatible(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo',
            title='foo', file=getData('plone.pdf'))]
        self.assertTrue(IFilesystemExporter(foo))
        self.assertTrue(IFilesystemImporter(foo))

class ImageReplacementTests(ReplacementTestCase):

    def afterSetUp(self):
        # don't interfere with catalog checks
        del self.folder['foo-image']

    def testAddImagePermission(self):
        permissions = permissionsFor('Image', 'plone.app.blob')
        self.assertTrue('ATContentTypes: Add Image' in permissions)

    def testCreateImageBlob(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('Image', 'foo')]
        foo.update(title="I'm blob", image=gif)
        # check content item
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(str(foo.getImage()), gif)
        # also make sure we're using blobs
        self.assertTrue(isinstance(foo, ATBlob), 'no atblob?')
        self.assertTrue(isinstance(foo.getField('image'), BlobField), 'no blob?')
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), gif)
        # let's also check the `getSize`, `tag` and `index_html` methods
        # as well as the size attributes
        self.assertEqual(foo.getSize(), (1, 1))
        self.assertEqual(foo.width, 1)
        self.assertEqual(foo.height, 1)
        self.assertTrue('/foo/image"' in foo.tag())
        # `index_html` should return a stream-iterator
        request = foo.REQUEST
        response = request.RESPONSE
        self.assertEqual(foo.index_html(request, response).next(), gif)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.headers['content-length'], '43')
        self.assertEqual(response.headers['content-type'], 'image/gif')

    def testImageBlobInterfaces(self):
        foo = self.folder[self.folder.invokeFactory('Image', 'foo')]
        self.assertTrue(atimage.IATImage.providedBy(foo), 'no IATImage?')
        self.assertTrue(atimage.IImageContent.providedBy(foo), 'no IImageContent?')
        self.assertTrue(IATBlobImage.providedBy(foo), 'no IATBlobImage?')
        if not IInterface.providedBy(Z2IATFile):    # this is zope < 2.12
            self.assertTrue(Z2IATImage.isImplementedBy(foo), 'no zope2 IATImage?')
            self.assertFalse(Z2IATFile.isImplementedBy(foo), 'zope2 IATFile?')

    def testImageMigration(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('ATImage', id='foo',
            title='an image', image=gif, subject=('foo', 'bar'),
            contributors=('me'))]
        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('Image')
        foo.reindexObject(idxs=('portal_type', ))
        # check to be migrated content
        self.assertTrue(isinstance(foo, ATImage), 'not an image?')
        self.assertEqual(foo.Title(), 'an image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me', ))
        # migrate & check migrated content item
        self.assertEqual(migrateATBlobImages(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (Image -> Image)\n')
        foo = self.folder['foo']
        self.assertTrue(isinstance(foo, ATBlob), 'not a blob?')
        self.assertTrue(isinstance(foo.getField('image'), BlobField), 'no blob?')
        self.assertEqual(foo.Title(), 'an image')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.getPortalTypeName(), 'Image')
        self.assertEqual(foo.Subject(), ('foo', 'bar'))
        self.assertEqual(foo.Contributors(), ('me', ))
        blob = foo.getImage().getBlob().open('r')
        self.assertEqual(blob.read(), gif)

    def testCatalogAfterImageMigration(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('ATImage', id='foo',
            title='an image', image=gif, subject=('foo', 'bar'),
            contributors=('me'))]

        # fake old content from before applying the replacement profile
        foo._setPortalTypeName('Image')
        foo.reindexObject(idxs=('portal_type', ))

        # remember the catalog data so it can be checked
        catalog = self.portal.portal_catalog
        rid = catalog(id='foo')[0].getRID()
        index_data = catalog.getIndexDataForRID(rid)
        meta_data = catalog.getMetadataForRID(rid)

        # migrate
        self.assertEqual(migrateATBlobImages(self.portal),
            'Migrating /plone/Members/test_user_1_/foo (Image -> Image)\n')
        foo = self.folder['foo']

        # Re-index date based indexes. It seems they're not properly re-indexed
        # after the migration is executed. Without this the tests may fail
        # due to to timing issues. Remember DateTimeIndex have resolution of
        # 1 minute.
        foo.reindexObject(idxs=('Date', 'created', 'modified', 'effective'))

        # check migrated content item
        brain = catalog(id='foo')[0]
        self.assertEqual(foo.UID(), brain.UID)
        self.assertEqual(foo.getObjSize(), brain.getObjSize)
        self.assertEqual(foo.getPortalTypeName(), brain.Type)

        # compare pre-migration and current catalog data...
        okay = ('meta_type', 'Type', 'object_provides', 'Language')
        for key, value in catalog.getIndexDataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(
                    index_data[key],
                    value,
                    'index: %s, old: %s, new: %s' % (key, index_data[key], value)
                )
        okay = ('meta_type', 'getIcon')
        for key, value in catalog.getMetadataForRID(brain.getRID()).items():
            if not key in okay:
                self.assertEqual(meta_data[key], value, 'meta: %s' % key)
        # also make sure the `Type` index has been updated correctly
        brains = catalog(Type='Image')
        self.assertEqual([b.getObject() for b in brains], [foo])

    def testModificationTimeDuringInlineImageMigration(self):
        foo = self.folder[self.folder.invokeFactory('Image', id='foo')]
        foo.schema['image'] = ImageField('image', storage=AnnotationStorage())
        foo.schema['image'].set(foo, getImage())
        # record the modification date before migration
        mod = foo.modified()
        # migrate using inline migrator
        migrate(self.portal, portal_type='Image', meta_type='ATBlob')
        # the modification date isn't changed by migration
        self.assertEqual(mod, foo.modified())
        # cleanup
        del foo.schema['image']

    def testOldScalesRemovedDuringInlineImageMigration(self):
        gif = getImage()
        foo = self.folder[self.folder.invokeFactory('Image', id='foo',
            title='an image', image=gif)]
        # fake an old ImageField in the class schema,
        # and store scales in AnnotationStorage
        foo.schema['image'] = ImageField('image', storage=AnnotationStorage())
        foo.schema['image'].set(foo, gif)
        isimage = lambda i: isinstance(i, Image)
        self.assertTrue(filter(isimage, IAnnotations(foo).values()))
        # migrate using inline migrator
        migrate(self.portal, portal_type='Image', meta_type='ATBlob')
        # make sure all scale annotations were removed
        self.assertFalse(filter(isimage, IAnnotations(foo).values()))
        # cleanup
        del foo.schema['image']

    def testImageDefaultSizes(self):
        image = self.folder[self.folder.invokeFactory('Image', 'foo')]
        sizes = image.getField('image').getAvailableSizes(image)
        self.assertTrue('mini' in sizes)
        self.assertEqual(sizes['mini'], (200, 200))

    def testImageGlobalSizes(self):
        image = self.folder[self.folder.invokeFactory('Image', 'foo')]
        changeAllowedSizes(self.portal, [u'foo 23:23'])
        sizes = image.getField('image').getAvailableSizes(image)
        self.assertEqual(sizes, {'foo': (23, 23)})

    def testImageCustomSizes(self):
        image = self.folder[self.folder.invokeFactory('Image', 'foo')]
        field = image.getField('image')
        # temporarily monkey-patch the field to avoid extensive test setup...
        original = field.sizes
        field.sizes = {'tiny': (42, 42)}
        sizes = image.getField('image').getAvailableSizes(image)
        self.assertEqual(sizes, {'tiny': (42, 42)})
        # and clean up again after outselves...
        field.sizes = original

    def testGetSizeOnEmptyImage(self):
        image = self.folder[self.folder.invokeFactory('Image', 'foo')]
        field = image.getField('image')
        self.assertEqual(field.getSize(image), (0, 0))

    def testGSContentCompatible(self):
        foo = self.folder[self.folder.invokeFactory('Image', 'foo')]
        self.assertTrue(IFilesystemExporter(foo))
        self.assertTrue(IFilesystemImporter(foo))

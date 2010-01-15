from plone.app.blob.tests.base import ReplacementTestCase   # import first!

from unittest import defaultTestLoader
from Products.ATContentTypes.interface import file as atfile
from Products.ATContentTypes.interface import image as atimage
from plone.app.blob.markings import unmarkAs


class MaintenanceViewTests(ReplacementTestCase):

    def afterSetUp(self):
        # ignore any generated logging output
        self.portal.REQUEST.RESPONSE.write = lambda x: x

    def testResetSubtypes(self):
        foo = self.folder[self.folder.invokeFactory('File', 'foo')]
        bar = self.folder[self.folder.invokeFactory('Image', 'bar')]
        # try to re-create the state of blob content created with pre-beta3
        unmarkAs(foo, 'File')
        unmarkAs(bar, 'Image')
        self.failIf(atfile.IFileContent.providedBy(foo), 'already IFileContent?')
        self.failIf(atimage.IImageContent.providedBy(bar), 'already IImageContent?')
        self.failIf(foo.Schema().getField('file'), 'has field "file"?')
        self.failIf(bar.Schema().getField('image'), 'has field "image"?')
        # then fix again using the respective view...
        maintenance = self.portal.unrestrictedTraverse('blob-maintenance')
        maintenance.resetSubtypes()
        self.failUnless(atfile.IFileContent.providedBy(foo), 'no IFileContent?')
        self.failUnless(atimage.IImageContent.providedBy(bar), 'no IImageContent?')
        self.failUnless(foo.Schema().getField('file'), 'no field "file"?')
        self.failUnless(bar.Schema().getField('image'), 'no field "image"?')

    def testUpdateTypeIndex(self):
        # conjure up incorrect catalog data...
        info = self.portal.portal_types.getTypeInfo('File')
        info.title = 'Foo'
        foo = self.folder[self.folder.invokeFactory('File', id='foo')]
        info.title = 'File'
        # make sure it's actually wrong...
        catalog = self.portal.portal_catalog
        self.failIf(catalog(Type='File'))
        self.failUnless(catalog(Type='Foo'))
        # fix using the maintenance view & check again...
        maintenance = self.portal.unrestrictedTraverse('blob-maintenance')
        maintenance.updateTypeIndex()
        self.assertEqual([b.getObject() for b in catalog(Type='File')], [foo])
        self.failIf(catalog(Type='Foo'))


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

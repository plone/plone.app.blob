from plone.app.blob.tests.base import ReplacementTestCase

from Products.Archetypes.public import BaseSchema, Schema, BaseContent
from Products.Archetypes.public import FileWidget, ImageWidget
from Products.Archetypes.public import registerType
from plone.app.blob.config import packageName, permissions
from plone.app.blob.field import FileField, ImageField
from plone.app.blob.tests.utils import getFile
from plone.app.blob.tests.base import changeAllowedSizes


SampleSchema = BaseSchema.copy() + Schema((

    FileField(
        name='foo',
        widget=FileWidget(label='File', description='a file')),

    ImageField(
        name='bar',
        widget=ImageWidget(label='Image', description='an image')),

    ImageField(
        name='hmm',
        sizes={'tiny': (42, 42)},
        widget=ImageWidget(label='Image', description='an image')),

))


class SampleType(BaseContent):

    portal_type = 'SampleType'
    schema = SampleSchema

permissions['SampleType'] = packageName + ': SampleType'
registerType(SampleType, packageName)


class BaseFieldTests(ReplacementTestCase):

    def create(self, id='foo2', **kw):
        container = self.folder
        obj = SampleType(id)
        obj = container[container._setObject(id, obj)]
        obj.initializeArchetype(**kw)
        return obj

    def testFileField(self):
        foo = self.create(foo=getFile('test.pdf'))
        self.assertEqual(str(foo.getFoo()), getFile('test.pdf').read())

    def testImageField(self):
        foo = self.create(bar=getFile('image.jpg'))
        self.assertEqual(str(foo.getBar()), getFile('image.jpg').read())
        self.assertTrue(foo.getField('bar').tag(foo).startswith('<img src'))

    def testImageDefaultSizes(self):
        image = self.create()
        sizes = image.getField('bar').getAvailableSizes(image)
        self.assertTrue('mini' in sizes)
        self.assertEqual(sizes['mini'], (200, 200))

    def testImageGlobalSizes(self):
        image = self.create()
        changeAllowedSizes(self.portal, [u'foo 23:23'])
        sizes = image.getField('bar').getAvailableSizes(image)
        self.assertEqual(sizes, {'foo': (23, 23)})

    def testImageCustomSizes(self):
        image = self.create()
        sizes = image.getField('hmm').getAvailableSizes(image)
        self.assertEqual(sizes, {'tiny': (42, 42)})

    def testGetSize(self):
        item = self.create(foo=getFile('test.pdf'), bar=getFile('image.jpg'))
        field = item.getField('foo')
        self.assertRaises(AttributeError, getattr, field, 'getSize')
        field = item.getField('bar')
        self.assertEqual(field.getSize(item), (500, 200))
        # empty images should return (0, 0)
        field = item.getField('hmm')
        self.assertEqual(field.getSize(item), (0, 0))

    def testSetFieldDefaultMime(self):
        item = self.create()
        file_ = getFile('test.pdf')
        item.setFoo(file_, filename='file.blubb', mimetype=None)
        self.assertEqual('application/pdf', item.getFoo().getContentType())

    def testStringDataRespectsFilename(self):
        item = self.create()
        file_ = getFile('test.pdf')
        item.setFoo(file_.read(), filename='file.xls', mimetype=None)
        self.assertEqual(
            'application/vnd.ms-excel',
            item.getFoo().getContentType()
            )

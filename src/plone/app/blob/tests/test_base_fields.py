from plone.app.blob.tests.base import BlobTestCase

from Products.Archetypes.public import BaseSchema, Schema, BaseContent
from Products.Archetypes.public import FileWidget, ImageWidget
from Products.Archetypes.public import registerType
from plone.app.blob.config import packageName, permissions
from plone.app.blob.field import FileField, ImageField
from plone.app.blob.tests.utils import getFile


SampleSchema = BaseSchema.copy() + Schema((

    FileField(
        name = 'foo',
        widget = FileWidget(label='File', description='a file')),

    ImageField(
        name = 'bar',
        widget = ImageWidget(label='Image', description='an image')),

))


class SampleType(BaseContent):

    portal_type = 'SampleType'
    schema = SampleSchema


permissions['SampleType'] = packageName + ': SampleType'
registerType(SampleType, packageName)



class BaseFieldTests(BlobTestCase):

    def create(self, id='foo', **kw):
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
        self.failUnless(foo.getField('bar').tag(foo).startswith('<img src'))


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)

# -*- coding: utf-8 -*-
from PIL.Image import open
from plone.app.blob.config import blobScalesAttr
from plone.app.blob.scale import BlobImageScaleHandler
from plone.app.blob.tests.base import changeAllowedSizes
from plone.app.blob.tests.base import ReplacementFunctionalTestCase
from plone.app.blob.tests.base import ReplacementTestCase
from plone.app.blob.tests.utils import getData
from plone.app.imaging.traverse import ImageTraverser
from six import StringIO
from ZODB.blob import Blob


class TraverseCounterMixin:

    def afterSetUp(self):
        self.counter = 0        # wrap `publishTraverse` with a counter
        self.original = ImageTraverser.publishTraverse

        def publishTraverse(adapter, request, name):
            self.counter += 1
            return self.original(adapter, request, name)
        ImageTraverser.publishTraverse = publishTraverse

    def beforeTearDown(self):
        ImageTraverser.publishTraverse = self.original


class BlobImageTraverseTests(TraverseCounterMixin, ReplacementTestCase):

    def testImageThumb(self):
        data = getData('image.gif')
        image = self.folder['foo-image']
        # make sure traversing works as is and with scaling
        traverse = self.layer['request'].traverseName
        self.assertEqual(traverse(image, 'image').data, data)
        sizes = image.getField('image').getAvailableSizes(image)
        self.assertTrue('thumb' in sizes.keys())
        thumb = traverse(image, 'image_thumb')
        self.assertEqual(thumb.getContentType(), 'image/gif')
        self.assertEqual(thumb.data[:6], 'GIF87a')
        width, height = sizes['thumb']
        self.assertEqual(thumb.width, width)
        self.assertEqual(thumb.height, height)
        # also check the generated tag
        url = image.absolute_url() + '/image_thumb'
        tag = '<img src="{0}" alt="an image" title="an image" height="{1}" width="{2}" />'  # noqa
        self.assertEqual(thumb.tag(), tag.format(url, height, width))
        # calling str(...) on the scale should return the tag
        self.assertEqual(str(thumb), thumb.tag())
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 2)

    def testCustomSizes(self):
        image = self.folder['foo-image']
        # set custom image sizes
        changeAllowedSizes(self.portal, [u'foo 23:23', u'bar 6:8'])
        # make sure traversing works with the new sizes
        traverse = self.layer['request'].traverseName
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.data[:6], 'GIF87a')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # also check the generated tag
        url = image.absolute_url() + '/image_foo'
        tag = '<img src="{0}" alt="an image" title="an image" height="23" width="23" />'  # noqa
        self.assertEqual(foo.tag(), tag.format(url))
        # and the other specified size
        bar = traverse(image, 'image_bar')
        self.assertEqual(bar.getContentType(), 'image/gif')
        self.assertEqual(bar.data[:6], 'GIF87a')
        self.assertEqual(bar.width, 6)
        self.assertEqual(bar.height, 6)
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 2)


class BlobImageScaleTests(ReplacementTestCase):

    def afterSetUp(self):
        self.counter = 0        # wrap `createScale` with a counter
        self.original = BlobImageScaleHandler.createScale

        def createScale(*args, **kw):
            self.counter += 1
            return self.original(*args, **kw)
        BlobImageScaleHandler.createScale = createScale

    def beforeTearDown(self):
        BlobImageScaleHandler.createScale = self.original

    def testBlobCreation(self):
        image = self.folder['foo-image']
        # make sure the scaled version is actually stored in a blob; we
        # also count invocations of `createScale`, which should be 0 still
        self.assertEqual(self.counter, 0)
        traverse = self.layer['request'].traverseName
        thumb = traverse(image, 'image_thumb')
        blob = getattr(image, blobScalesAttr)['image']['thumb']['blob']
        self.assertTrue(isinstance(blob, Blob), 'no blob?')
        self.assertEqual(blob.open('r').read(), thumb.data)
        self.assertEqual(self.counter, 1)
        # the scale was created, now let's access it a few more times
        thumb = traverse(image, 'image_thumb')
        thumb = traverse(image, 'image_thumb')
        self.assertEqual(self.counter, 1)

    def testScaleInvalidation(self):
        image = self.folder['foo-image']
        # first view the thumbnail of the original image
        traverse = self.layer['request'].traverseName
        thumb1 = traverse(image, 'image_thumb')
        # now upload a new one and make sure the thumbnail has changed
        image.update(image=getData('image.jpg'))
        thumb2 = traverse(image, 'image_thumb')
        self.assertFalse(thumb1.data == thumb2.data, 'thumb not updated?')

    def testCustomSizeChange(self):
        image = self.folder['foo-image']
        # set custom image sizes & view a scale
        changeAllowedSizes(self.portal, [u'foo 23:23'])
        traverse = self.layer['request'].traverseName
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # now let's update the scale dimensions, after which the scale
        # should still be the same...
        changeAllowedSizes(self.portal, [u'foo 42:42'])
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # we first need to trigger recreation of all scales...
        self.portal.portal_atct.recreateImageScales()
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 42)
        self.assertEqual(foo.height, 42)


class BlobImagePublisherTests(
    TraverseCounterMixin,
    ReplacementFunctionalTestCase,
):

    def testPublishThumb(self):
        data = getData('image.gif')
        # make sure traversing works as is and with scaling
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        # first the image itself...
        response = self.publish(base + '/foo-image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # then the field without a scale name
        response = self.publish(base + '/foo-image/image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # and last a scaled version
        response = self.publish(
            base + '/foo-image/image_thumb', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody()[:6], 'GIF87a')
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 9)

    def testPublishCustomSize(self):
        # set custom image sizes
        changeAllowedSizes(self.portal, [u'foo 23:23'])
        # make sure traversing works as expected
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        response = self.publish(
            base + '/foo-image/image_foo', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        foo = open(StringIO(response.getBody()))
        self.assertEqual(foo.format, 'GIF')
        self.assertEqual(foo.size, (23, 23))
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 3)


class BlobAdapterTests(ReplacementTestCase):

    def afterSetUp(self):
        self.image = self.folder['foo-image']
        self.field = self.image.getField('image')
        self.handler = BlobImageScaleHandler(self.field)
        changeAllowedSizes(self.portal, [u'foo 60:60'])

    def testCreateScale(self):
        foo = self.handler.createScale(self.image, 'foo', 100, 80)
        self.assertEqual(foo['id'], 'image_foo')
        self.assertEqual(foo['content_type'], 'image/gif')
        self.assertEqual(foo['data'][:6], 'GIF87a')

    def testCreateScaleWithZeroWidth(self):
        foo = self.handler.createScale(self.image, 'foo', 100, 0)
        self.assertEqual(foo, None)

    def testCreateScaleWithoutData(self):
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='image')]
        field = image.getField('image')
        handler = BlobImageScaleHandler(field)
        foo = handler.createScale(image, 'foo', 100, 80)
        self.assertEqual(foo, None)

    def testGetScale(self):
        foo = self.handler.getScale(self.image, 'foo')
        self.assertEqual(foo.getId(), 'image_foo')
        self.assertEqual(foo.getContentType(), 'image/gif')
        self.assertEqual(foo.data[:6], 'GIF87a')
        self.assertEqual(foo.width, 60)
        self.assertEqual(foo.height, 60)

    def testGetUnknownScale(self):
        foo = self.handler.getScale(self.image, 'foo?')
        self.assertEqual(foo, None)


class BlobAdapterPublisherTests(ReplacementTestCase):

    def afterSetUp(self):
        self.original = BlobImageScaleHandler.getScale

        def getScale(adapter, instance, scale):
            self.counter += 1
            return self.original(adapter, instance, scale)
        BlobImageScaleHandler.getScale = getScale

    def beforeTearDown(self):
        # undo the evil monkey patching...
        # and make sure the traversal adapter was call in fact
        BlobImageScaleHandler.getScale = self.original

    def testScalingViaBlobAdapter(self):
        # make sure `getScale` of the blob-specific scale handler is called
        self.counter = 0
        data = getData('image.gif')
        # make sure traversing works as expected
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        response = self.publish(base + '/foo-image/image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        self.assertEqual(self.counter, 1)

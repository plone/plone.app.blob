from unittest import TestSuite, makeSuite
from plone.app.blob.tests.base import ReplacementTestCase
from plone.app.blob.tests.base import ReplacementFunctionalTestCase
from plone.app.blob.tests.utils import getData
from plone.app.imaging.traverse import ImageTraverser
from plone.app.blob.scale import BlobImageScaleHandler
from plone.app.blob.config import blobScalesAttr
from ZODB.blob import Blob
from StringIO import StringIO
from PIL.Image import open


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
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        # make sure traversing works as is and with scaling
        traverse = folder.REQUEST.traverseName
        self.assertEqual(traverse(image, 'image').data, data)
        sizes = image.getField('image').getAvailableSizes(image)
        self.failUnless('thumb' in sizes.keys())
        thumb = traverse(image, 'image_thumb')
        self.assertEqual(thumb.getContentType(), 'image/png')
        self.assertEqual(thumb.data[:4], '\x89PNG')
        width, height = sizes['thumb']
        self.assertEqual(thumb.width, width)
        self.assertEqual(thumb.height, height)
        # also check the generated tag
        url = image.absolute_url() + '/image_thumb'
        tag = '<img src="%s" alt="foo" title="foo" height="%d" width="%d" />'
        self.assertEqual(thumb.tag(), tag % (url, height, width))
        # calling str(...) on the scale should return the tag
        self.assertEqual(str(thumb), thumb.tag())
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 2)

    def testCustomSizes(self):
        data = getData('image.gif')
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        # set custom image sizes
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23', 'bar 6:8'])
        # make sure traversing works with the new sizes
        traverse = folder.REQUEST.traverseName
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.getContentType(), 'image/png')
        self.assertEqual(foo.data[:4], '\x89PNG')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # also check the generated tag
        url = image.absolute_url() + '/image_foo'
        tag = '<img src="%s" alt="foo" title="foo" height="23" width="23" />'
        self.assertEqual(foo.tag(), tag % url)
        # and the other specified size
        bar = traverse(image, 'image_bar')
        self.assertEqual(bar.getContentType(), 'image/png')
        self.assertEqual(bar.data[:4], '\x89PNG')
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
        data = getData('image.gif')
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        # make sure the scaled version is actually stored in a blob; we
        # also count invocations of `createScale`, which should be 0 still
        self.assertEqual(self.counter, 0)
        traverse = folder.REQUEST.traverseName
        thumb = traverse(image, 'image_thumb')
        blob = getattr(image, blobScalesAttr)['image']['thumb']['blob']
        self.failUnless(isinstance(blob, Blob), 'no blob?')
        self.assertEqual(blob.open('r').read(), thumb.data)
        self.assertEqual(self.counter, 1)
        # the scale was created, now let's access it a few more times
        thumb = traverse(image, 'image_thumb')
        thumb = traverse(image, 'image_thumb')
        self.assertEqual(self.counter, 1)

    def testScaleInvalidation(self):
        data = getData('image.gif')
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        # first view the thumbnail of the original image
        traverse = folder.REQUEST.traverseName
        thumb1 = traverse(image, 'image_thumb')
        # now upload a new one and make sure the thumbnail has changed
        image.update(image=getData('image.jpg'))
        traverse = folder.REQUEST.traverseName
        thumb2 = traverse(image, 'image_thumb')
        self.failIf(thumb1.data == thumb2.data, 'thumb not updated?')

    def testCustomSizeChange(self):
        data = getData('image.gif')
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        # set custom image sizes & view a scale
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        traverse = folder.REQUEST.traverseName
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # now let's update the scale dimensions, after which the scale
        # should still be the same...
        iprops.manage_changeProperties(allowed_sizes=['foo 42:42'])
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # we first need to trigger recreation of all scales...
        self.portal.portal_atct.recreateImageScales()
        foo = traverse(image, 'image_foo')
        self.assertEqual(foo.width, 42)
        self.assertEqual(foo.height, 42)


class BlobImagePublisherTests(TraverseCounterMixin, ReplacementFunctionalTestCase):

    def testPublishThumb(self):
        data = getData('image.gif')
        self.folder.invokeFactory('Image', id='foo', image=data)
        # make sure traversing works as is and with scaling
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        # first the image itself...
        response = self.publish(base + '/foo', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # then the field without a scale name
        response = self.publish(base + '/foo/image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # and last a scaled version
        response = self.publish(base + '/foo/image_thumb', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody()[:4], '\x89PNG')
        self.assertEqual(response.getHeader('Content-Type'), 'image/png')
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 9)

    def testPublishCustomSize(self):
        data = getData('image.gif')
        self.folder.invokeFactory('Image', id='foo', image=data)
        # set custom image sizes
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        # make sure traversing works as expected
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        response = self.publish(base + '/foo/image_foo', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        foo = open(StringIO(response.getBody()))
        self.assertEqual(foo.format, 'PNG')
        self.assertEqual(foo.size, (23, 23))
        # make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 3)


class BlobAdapterTests(ReplacementTestCase):

    def afterSetUp(self):
        data = getData('image.gif')
        folder = self.folder
        self.image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        self.field = self.image.getField('image')
        self.handler = BlobImageScaleHandler(self.field)
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 60:60'])

    def testCreateScale(self):
        foo = self.handler.createScale(self.image, 'foo', 100, 80)
        self.assertEqual(foo['id'], 'image_foo')
        self.assertEqual(foo['content_type'], 'image/png')
        self.assertEqual(foo['data'][:4], '\x89PNG')

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
        self.assertEqual(foo.getContentType(), 'image/png')
        self.assertEqual(foo.data[:4], '\x89PNG')
        self.assertEqual(foo.width, 60)
        self.assertEqual(foo.height, 60)

    def testGetUnknownScale(self):
        foo = self.handler.getScale(self.image, 'foo?')
        self.assertEqual(foo, None)


class BlobAdapterPublisherTests(ReplacementFunctionalTestCase):

    def testScalingViaBlobAdapter(self):
        # make sure `getScale` of the blob-specific scale handler is called
        self.counter = 0
        original = BlobImageScaleHandler.getScale
        def getScale(adapter, instance, scale):
            self.counter += 1
            return original(adapter, instance, scale)
        BlobImageScaleHandler.getScale = getScale
        data = getData('image.gif')
        self.folder.invokeFactory('Image', id='foo', image=data)
        # make sure traversing works as expected
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        response = self.publish(base + '/foo/image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), data)
        # undo the evil monkey patching...
        BlobImageScaleHandler.getScale = original
        # and make sure the traversal adapter was call in fact
        self.assertEqual(self.counter, 1)


def test_suite():
    return TestSuite([
        makeSuite(BlobImageTraverseTests),
        makeSuite(BlobImageScaleTests),
        makeSuite(BlobImagePublisherTests),
        makeSuite(BlobAdapterTests),
        makeSuite(BlobAdapterPublisherTests),
    ])

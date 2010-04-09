from unittest import TestSuite, makeSuite
from plone.app.blob.tests.base import ReplacementTestCase
from plone.app.blob.tests.base import ReplacementFunctionalTestCase
from plone.app.imaging.tests.base import ImagingTestCaseMixin
from plone.app.imaging.scaling import ImageScaling
from re import match


class ImageTraverseTests(ReplacementTestCase, ImagingTestCaseMixin):

    def afterSetUp(self):
        self.data = self.getImage()
        self.image = self.folder[self.folder.invokeFactory('Image', id='foo',
            image=self.data)]
        field = self.image.getField('image')
        self.available = field.getAvailableSizes(self.image)

    def traverse(self, path=''):
        view = self.image.unrestrictedTraverse('@@images')
        stack = path.split('/')
        name = stack.pop(0)
        tag = view.traverse(name, stack)
        base = self.image.absolute_url()
        expected = r'<img src="%s/@@images/([-0-9a-f]{36}).(jpeg|gif|png)" ' \
            r'alt="foo" title="foo" height="(\d+)" width="(\d+)" />' % base
        groups = match(expected, tag).groups()
        self.failUnless(groups, tag)
        uid, ext, height, width = groups
        return uid, ext, int(width), int(height)

    def testImageThumb(self):
        self.failUnless('thumb' in self.available.keys())
        uid, ext, width, height = self.traverse('image/thumb')
        self.assertEqual((width, height), self.available['thumb'])
        self.assertEqual(ext, 'jpeg')

    def testCustomSizes(self):
        # set custom image sizes
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        # make sure traversing works with the new sizes
        uid, ext, width, height = self.traverse('image/foo')
        self.assertEqual(width, 23)
        self.assertEqual(height, 23)

    def testScaleInvalidation(self):
        # first view the thumbnail of the original image
        uid1, ext, width1, height1 = self.traverse('image/thumb')
        # now upload a new one and make sure the thumbnail has changed
        self.image.update(image=self.getImage('image.jpg'))
        uid2, ext, width2, height2 = self.traverse('image/thumb')
        self.assertNotEqual(uid1, uid2, 'thumb not updated?')
        # the height also differs as the original image had a size of 200, 200
        # whereas the updated one has 500, 200...
        self.assertEqual(width1, width2)
        self.assertNotEqual(height1, height2)

    def testCustomSizeChange(self):
        # set custom image sizes & view a scale
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        uid1, ext, width, height = self.traverse('image/foo')
        self.assertEqual(width, 23)
        self.assertEqual(height, 23)
        # now let's update the scale dimensions, after which the scale
        # should also have been updated...
        iprops.manage_changeProperties(allowed_sizes=['foo 42:42'])
        uid2, ext, width, height = self.traverse('image/foo')
        self.assertEqual(width, 42)
        self.assertEqual(height, 42)
        self.assertNotEqual(uid1, uid2, 'scale not updated?')


class ImagePublisherTests(ReplacementFunctionalTestCase, ImagingTestCaseMixin):

    def afterSetUp(self):
        data = self.getImage()
        folder = self.folder
        foo = folder[folder.invokeFactory('Image', id='foo', image=data)]
        self.view = foo.unrestrictedTraverse('@@images')

    def testPublishScaleViaUID(self):
        scale = self.view.scale('image', width=64, height=64)
        # make sure the referenced image scale is available
        url = scale.url.replace('http://nohost', '')
        response = self.publish(url, basic=self.getCredentials())
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'image/jpeg')
        self.assertImage(response.getBody(), 'JPEG', (64, 64))

    def testPublishThumbViaUID(self):
        scale = self.view.scale('image', 'thumb')
        # make sure the referenced image scale is available
        url = scale.url.replace('http://nohost', '')
        response = self.publish(url, basic=self.getCredentials())
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'image/jpeg')
        self.assertImage(response.getBody(), 'JPEG', (128, 128))

    def testPublishCustomSizeViaUID(self):
        # set custom image sizes
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        scale = self.view.scale('image', 'foo')
        # make sure the referenced image scale is available
        url = scale.url.replace('http://nohost', '')
        response = self.publish(url, basic=self.getCredentials())
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'image/jpeg')
        self.assertImage(response.getBody(), 'JPEG', (23, 23))

    def testPublishThumbViaName(self):
        # make sure traversing works as is and with scaling
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        # first the field without a scale name
        response = self.publish(base + '/foo/@@images/image', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getBody(), self.getImage())
        self.assertEqual(response.getHeader('Content-Type'), 'image/gif')
        # and last a scaled version
        response = self.publish(base + '/foo/@@images/image/thumb', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertEqual(response.getHeader('Content-Type'), 'image/jpeg')
        self.assertImage(response.getBody(), 'JPEG', (128, 128))

    def testPublishCustomSizeViaName(self):
        # set custom image sizes
        iprops = self.portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        # make sure traversing works as expected
        base = '/'.join(self.folder.getPhysicalPath())
        credentials = self.getCredentials()
        response = self.publish(base + '/foo/@@images/image/foo', basic=credentials)
        self.assertEqual(response.getStatus(), 200)
        self.assertImage(response.getBody(), 'JPEG', (23, 23))


class ScalesAdapterTests(ReplacementTestCase, ImagingTestCaseMixin):

    def afterSetUp(self):
        data = self.getImage()
        folder = self.folder
        self.image = folder[folder.invokeFactory('Image', id='foo', image=data)]
        self.adapter = ImageScaling(self.image, None)
        self.iprops = self.portal.portal_properties.imaging_properties
        self.iprops.manage_changeProperties(allowed_sizes=['foo 60:60'])

    def testCreateScale(self):
        foo = self.adapter.scale('image', width=100, height=80)
        self.failUnless(foo.uid)
        self.assertEqual(foo.mimetype, 'image/jpeg')
        self.assertEqual(foo.width, 80)
        self.assertEqual(foo.height, 80)
        self.assertImage(foo.data, 'JPEG', (80, 80))

    def testCreateScaleWithoutData(self):
        folder = self.folder
        image = folder[folder.invokeFactory('Image', id='image')]
        adapter = ImageScaling(image, None)
        foo = adapter.scale('image', width=100, height=80)
        self.assertEqual(foo, None)

    def testGetScaleByName(self):
        foo = self.adapter.scale('image', scale='foo')
        self.failUnless(foo.uid)
        self.assertEqual(foo.mimetype, 'image/jpeg')
        self.assertEqual(foo.width, 60)
        self.assertEqual(foo.height, 60)
        self.assertImage(foo.data, 'JPEG', (60, 60))

    def testGetUnknownScale(self):
        foo = self.adapter.scale('image', scale='foo?')
        self.assertEqual(foo, None)

    def testScaleInvalidation(self):
        # first get the scale of the original image
        foo1 = self.adapter.scale('image', scale='foo')
        # now upload a new one and make sure the scale has changed
        self.image.update(image=self.getImage('image.jpg'))
        foo2 = self.adapter.scale('image', scale='foo')
        self.failIf(foo1.data == foo2.data, 'scale not updated?')

    def testCustomSizeChange(self):
        # set custom image sizes & view a scale
        self.iprops.manage_changeProperties(allowed_sizes=['foo 23:23'])
        foo = self.adapter.scale('image', scale='foo')
        self.assertEqual(foo.width, 23)
        self.assertEqual(foo.height, 23)
        # now let's update the scale dimensions, after which the scale
        # shouldn't be the same...
        self.iprops.manage_changeProperties(allowed_sizes=['foo 42:42'])
        foo = self.adapter.scale('image', scale='foo')
        self.assertEqual(foo.width, 42)
        self.assertEqual(foo.height, 42)

    def testScaleThatCausesErrorsCanBeSuppressed(self):
        field = self.image.getField('image')
        field.swallowResizeExceptions = False
        self.assertRaises(Exception, self.adapter.scale, 'image')
        # scaling exceptions should be "swallowed" when set on the field...
        field.swallowResizeExceptions = True
        self.assertEqual(self.adapter.scale('image'), None)


def test_suite():
    return TestSuite([
        makeSuite(ImageTraverseTests),
        makeSuite(ImagePublisherTests),
        makeSuite(ScalesAdapterTests),
    ])

from unittest import TestSuite, makeSuite
from plone.app.blob.tests.base import ReplacementFunctionalTestCase
from plone.app.blob.tests.utils import getImage
from plone.app.blob.interfaces import IATBlobImage
from StringIO import StringIO


class WebDavTests(ReplacementFunctionalTestCase):

    def testWebDavUpload(self):
        image = StringIO(getImage())
        image.filename = 'original.gif'
        base = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(base + '/image', request_method='PUT',
            stdin=image, basic=self.getCredentials(),
            env={'CONTENT_TYPE': 'image/gif'})
        self.assertEqual(response.getStatus(), 201)
        self.failUnless('image' in self.folder.objectIds())
        obj = self.folder.image
        self.assertEqual(obj.getPortalTypeName(), 'Image')
        self.failUnless(IATBlobImage.providedBy(obj), 'no blob?')
        self.assertEqual(str(obj.getField('image').get(obj)), image.getvalue())
        # on initial (webdav) upload no filename is set by the client,
        # so it should end up being equal to the last path/url component...
        self.assertEqual(obj.getFilename(), 'image')

    def testWebDavUpdate(self):
        image = StringIO(getImage())
        image.filename = 'original.gif'
        self.folder.invokeFactory('Image', id='foo',
            title='an image', image=image)
        base = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(base + '/foo', request_method='PUT',
            stdin=image, basic=self.getCredentials(),
            env={'CONTENT_TYPE': 'image/gif'})
        self.assertEqual(response.getStatus(), 204)
        self.failUnless('foo' in self.folder.objectIds())
        self.assertEqual(self.folder.foo.getId(), 'foo')
        self.assertEqual(self.folder.foo.Title(), 'an image')
        # as opposed to during file upload, editing a file via webdav (e.g.
        # using the "external editor" feature) should not change the filename
        self.assertEqual(self.folder.foo.getFilename(), 'original.gif')


def test_suite():
    return TestSuite([
        makeSuite(WebDavTests),
    ])

# -*- coding: utf-8 -*-
from plone.app.blob.interfaces import IATBlobImage
from plone.app.blob.tests.base import ReplacementTestCase
from plone.app.blob.tests.utils import getImage
from six import StringIO


class WebDavTests(ReplacementTestCase):

    def testWebDavUpload(self):
        image = StringIO(getImage())
        image.filename = 'original.gif'
        base = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(base + '/image', request_method='PUT',
                                stdin=image, basic=self.getCredentials(),
                                env={'CONTENT_TYPE': 'image/gif'})
        self.assertEqual(response.getStatus(), 201)
        self.assertTrue('image' in self.folder.objectIds())
        obj = self.folder.image
        self.assertEqual(obj.getPortalTypeName(), 'Image')
        self.assertTrue(IATBlobImage.providedBy(obj), 'no blob?')
        self.assertEqual(str(obj.getField('image').get(obj)), image.getvalue())
        # on initial (webdav) upload no filename is set by the client,
        # so it should end up being equal to the last path/url component...
        self.assertEqual(obj.getFilename(), 'image')

    def testWebDavUpdate(self):
        image = StringIO(getImage())
        image.filename = 'original.gif'
        base = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(base + '/foo-image', request_method='PUT',
                                stdin=image, basic=self.getCredentials(),
                                env={'CONTENT_TYPE': 'image/gif'})
        self.assertEqual(response.getStatus(), 204)
        self.assertTrue('foo-image' in self.folder.objectIds())
        fooimage = self.folder['foo-image']
        self.assertEqual(fooimage.getId(), 'foo-image')
        self.assertEqual(fooimage.Title(), 'an image')
        # as opposed to during file upload, editing a file via webdav (e.g.
        # using the "external editor" feature) should not change the filename
        self.assertEqual(fooimage.getFilename(), 'original.gif')

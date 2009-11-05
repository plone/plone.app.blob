from unittest import defaultTestLoader
from plone.app.blob.tests.base import ReplacementFunctionalTestCase
from plone.app.blob.tests.utils import getImage
from plone.app.blob.interfaces import IATBlobImage
from StringIO import StringIO


class WebDavTests(ReplacementFunctionalTestCase):

    def testWebDavUpload(self):
        image = getImage()
        base = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(base + '/image', request_method='PUT',
            stdin=StringIO(image), basic=self.getCredentials(),
            env={'CONTENT_TYPE': 'image/gif'})
        self.assertEqual(response.getStatus(), 201)
        self.failUnless('image' in self.folder.objectIds())
        obj = self.folder.image
        self.assertEqual(obj.getPortalTypeName(), 'Image')
        self.failUnless(IATBlobImage.providedBy(obj), 'no blob?')
        self.assertEqual(str(obj.getField('image').get(obj)), image)


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

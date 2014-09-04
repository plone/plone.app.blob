from unittest import TestCase

from plone.app.blob.tests.utils import getFile
from plone.app.blob.utils import getImageSize
from plone.app.blob import utils


class UtilityTests(TestCase):

    def testImageSizes(self):
        self.assertEqual(getImageSize(getFile('image.gif')), (200, 200))
        self.assertEqual(getImageSize(getFile('image.png')), (500, 200))
        self.assertEqual(getImageSize(getFile('image.jpg')), (500, 200))

    def testImageSizesWithoutPIL(self):
        hasPIL = utils.hasPIL
        utils.hasPIL = False
        self.assertEqual(getImageSize(getFile('image.gif')), (200, 200))
        self.assertEqual(getImageSize(getFile('image.png')), (500, 200))
        # the fallback method cannot handle jpegs properly
        self.assertEqual(getImageSize(getFile('image.jpg')), (-1, -1))
        utils.hasPIL = hasPIL

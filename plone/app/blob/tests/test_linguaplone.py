from plone.app.blob.tests.base import BlobLinguaTestCase    # import first!
from unittest import TestSuite, defaultTestLoader

from plone.app.blob.tests.utils import getData, hasLinguaPlone


class LinguaTests(BlobLinguaTestCase):

    def testCreateBlobelFish(self):
        self.setRoles(('Manager',))
        guide = getData('plone.pdf')
        foo = self.folder[self.folder.invokeFactory('BlobelFish', 'flobby')]
        foo.update(title='Me fish.', guide=guide)
        # check content item
        self.assertEqual(foo.getPortalTypeName(), 'BlobelFish')
        self.assertEqual(foo.getContentType(), 'application/pdf')
        self.assertEqual(str(foo.getGuide()), guide)


def test_suite():
    if hasLinguaPlone():
        return defaultTestLoader.loadTestsFromName(__name__)
    else:
        return TestSuite()


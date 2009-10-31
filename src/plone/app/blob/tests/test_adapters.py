from unittest import defaultTestLoader
from ZODB.blob import Blob
from OFS.Image import File
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.tests.base import BlobTestCase
from plone.app.blob.tests.utils import getFile


class AdapterTests(BlobTestCase):

    def testBlobbableOFSFile(self):
        obj = File('foo', 'Foo', getFile('plone.pdf'), 'application/pdf')
        obj.filename = 'foo.pdf'
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEquals(target.open('r').read(),
            getFile('plone.pdf').read())
        self.assertEquals(blobbable.filename(), 'foo.pdf')
        self.assertEquals(blobbable.mimetype(), 'application/pdf')


def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

from unittest import defaultTestLoader
from ZODB.blob import Blob
from OFS.Image import File, Image
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.file import ATFile
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.tests.base import BlobTestCase
from plone.app.blob.tests.utils import getFile, getImage
from StringIO import StringIO
from xmlrpclib import Binary


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

    def testBlobbableOFSFileWithoutFileName(self):
        obj = File('foo', 'Foo', getFile('plone.pdf'), 'application/pdf')
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEquals(target.open('r').read(),
            getFile('plone.pdf').read())
        self.assertEquals(blobbable.filename(), '')
        self.assertEquals(blobbable.mimetype(), 'application/pdf')

    def testBlobbableOFSImage(self):
        gif = getImage()
        obj = Image('foo', 'Foo', StringIO(gif))
        obj.filename = 'foo.gif'
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEquals(target.open('r').read(), gif)
        self.assertEquals(blobbable.filename(), 'foo.gif')
        self.assertEquals(blobbable.mimetype(), 'image/gif')

    def testBlobbableEmptyATImage(self):
        obj = ATImage('foo')
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)

    def testBlobbableEmptyATFile(self):
        obj = ATFile('foo')
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)

    def testBlobbableBinaryFile(self):
        self.assertEquals(True, False)

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)

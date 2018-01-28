# -*- coding: utf-8 -*-
from OFS.Image import File
from OFS.Image import Image
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.tests.base import BlobTestCase
from plone.app.blob.tests.utils import getFile
from plone.app.blob.tests.utils import getImage
from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.image import ATImage
from six import StringIO
from six.moves.xmlrpc_client import Binary
from ZODB.blob import Blob

import os


class AdapterTests(BlobTestCase):

    def testBlobbableOFSFile(self):
        obj = File('foo', 'Foo', getFile('plone.pdf'), 'application/pdf')
        obj.filename = 'foo.pdf'
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEqual(target.open('r').read(),
                         getFile('plone.pdf').read())
        self.assertEqual(blobbable.filename(), 'foo.pdf')
        self.assertEqual(blobbable.mimetype(), 'application/pdf')

    def testBlobbableOFSFileWithoutFileName(self):
        obj = File('foo', 'Foo', getFile('plone.pdf'), 'application/pdf')
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEqual(target.open('r').read(),
                         getFile('plone.pdf').read())
        self.assertEqual(blobbable.filename(), '')
        self.assertEqual(blobbable.mimetype(), 'application/pdf')

    def testBlobbableOFSImage(self):
        gif = getImage()
        obj = Image('foo', 'Foo', StringIO(gif))
        obj.filename = 'foo.gif'
        blobbable = IBlobbable(obj)
        target = Blob()
        blobbable.feed(target)
        self.assertEqual(target.open('r').read(), gif)
        self.assertEqual(blobbable.filename(), 'foo.gif')
        self.assertEqual(blobbable.mimetype(), 'image/gif')

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
        _file = os.path.join(os.path.dirname(__file__), 'data', 'image.gif')
        with open(_file, 'rb') as f:
            obj = Binary(f)
            obj.filename = 'image.gif'
            blobbable = IBlobbable(obj)
            target = Blob()
            blobbable.feed(target)
            self.assertEqual(target.open('r').read(),
                             getFile('image.gif').read())
            self.assertEqual(blobbable.filename(), 'image.gif')
            self.assertEqual(blobbable.mimetype(), 'image/gif')

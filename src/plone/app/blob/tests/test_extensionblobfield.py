# -*- coding: utf-8 -*-
from plone.app.blob.tests.base import BlobSchemaExtenderTestCase
from plone.app.blob.tests.utils import hasSchemaExtender
from unittest import defaultTestLoader
from unittest import TestSuite


class ExtenderTests(BlobSchemaExtenderTestCase):

    def testImageOnDocument(self):
        """Test that adding an image blob field to a document doesn't
        error for lack of EXIF helper functions"""
        document_id = self.folder.invokeFactory('Document', id='doc')
        document = self.folder[document_id]
        document.Schema().get('image').set(document, 'f')

    def testImageOnImage(self):
        """Test that an extension image field works on a class that has image
        helper methods"""
        img_id = self.folder.invokeFactory('Image', id='img')
        img = self.folder[img_id]
        img.Schema().get('new_image').set(img, 'f')


def test_suite():
    if hasSchemaExtender():
        return defaultTestLoader.loadTestsFromName(__name__)
    else:
        return TestSuite()

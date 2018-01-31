# -*- coding: utf-8 -*-
from plone.app.blob.tests.layer import BlobLayer
from plone.app.blob.tests.layer import BlobLinguaLayer
from plone.app.blob.tests.layer import BlobReplacementLayer
from plone.app.blob.tests.layer import BlobSchemaExtenderLayer
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing.bbb import PloneTestCase
from plone.registry.interfaces import IRegistry
from plone.testing.z2 import Browser
from zope.component import queryUtility


class BlobTestCase(PloneTestCase):
    """ base class for integration tests """

    layer = BlobLayer

    def getCredentials(self):
        return '{0}:{1}'.format(TEST_USER_NAME, TEST_USER_PASSWORD)

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser(self.layer['app'])
        if loggedIn:
            auth = 'Basic {0}'.format(self.getCredentials())
            browser.addHeader('Authorization', auth)
        return browser


BlobFunctionalTestCase = BlobTestCase


class ReplacementTestCase(BlobTestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


ReplacementFunctionalTestCase = ReplacementTestCase


class BlobSchemaExtenderTestCase(PloneTestCase):
    """ base class for schemaextender tests """

    layer = BlobSchemaExtenderLayer


class BlobLinguaTestCase(PloneTestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


class BlobLinguaFunctionalTestCase(PloneTestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


def changeAllowedSizes(portal, sizes):
    try:
        iprops = portal.portal_properties.imaging_properties
        iprops.manage_changeProperties(allowed_sizes=sizes)
    except AttributeError:
        # Plone 5, no longer stored here
        registry = queryUtility(IRegistry)
        from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
        settings = registry.forInterface(
            IImagingSchema, prefix='plone', check=False)
        settings.allowed_sizes = sizes

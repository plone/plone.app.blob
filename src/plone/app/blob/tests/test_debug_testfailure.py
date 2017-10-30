# -*- coding: utf-8 -*-
from plone.app.blob.tests.utils import getFile
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing import z2
from plone.testing.z2 import Browser

import io
import os.path
import unittest



class PloneAppBlobLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):

        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.blob')

    def setUpPloneSite(self, portal):
        # install Products.ATContentTypes manually if profile is available
        # (this is only needed for Plone >= 5)
        profiles = [x['id'] for x in portal.portal_setup.listProfileInfo()]
        if 'Products.ATContentTypes:default' in profiles:
            applyProfile(portal, 'Products.ATContentTypes:default')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'plone.app.blob')
        z2.uninstallProduct(app, 'Products.ATContentTypes')
        z2.uninstallProduct(app, 'Products.Archetypes')


PLONE_APP_BLOB_FIXTURE = PloneAppBlobLayer()
PLONE_APP_BLOB_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_APP_BLOB_FIXTURE,),
    name='PloneAppBlob:Functional'
)


class TestGIFImages(unittest.TestCase):

    layer = PLONE_APP_BLOB_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal.acl_users.userFolderAddUser(SITE_OWNER_NAME,
                                                SITE_OWNER_PASSWORD,
                                                ['Manager'],
                                                [])
        login(self.portal, SITE_OWNER_NAME)
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic {0}:{1}'.format(SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_gifimages(self):
        """Uploading a gif fails.
        """
        self.browser.open(self.portal.absolute_url())
        self.browser.getLink(url='createObject?type_name=Image').click()
        self.assertIn('/portal_factory/Image/image', self.browser.url)
        self.browser.getControl(name='title').value = 'Bar'
        control = self.browser.getControl(name='image_file')
        image_path = os.path.join(os.path.dirname(__file__), 'data/image.gif')
        control.add_file(io.FileIO(image_path), None, 'image.gif')
        self.browser.getControl('Save').click()

        self.assertEqual(self.browser.url, 'http://nohost/plone/bar/view')
        image = self.portal['bar']
        original = len(image.getImage().data)

        # Now edit it. First store the current image,
        # however, so we can check it was actually updated:
        self.browser.getLink('Edit').click()
        self.browser.getControl(name='title').value = 'Foobar'
        self.browser.getControl('Replace with new image').selected = True
        control = self.browser.getControl(name='image_file')
        image_path = os.path.join(os.path.dirname(__file__), 'data/image.png')
        control.add_file(io.FileIO(image_path), None, 'image.png')
        self.browser.getControl('Save').click()
        self.assertNotEqual(original, len(image.getImage().data))

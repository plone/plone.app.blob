from unittest import TestSuite
from zope.testing import doctest
from Testing.ZopeTestCase import ZopeDocFileSuite
from plone.app.blob.tests.base import BlobFunctionalTestCase
from plone.app.blob.tests.base import ReplacementFunctionalTestCase

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    return TestSuite((
        ZopeDocFileSuite(
           'README.txt', package='plone.app.blob',
           test_class=BlobFunctionalTestCase, optionflags=optionflags),
        ZopeDocFileSuite(
           'replacement-types.txt', package='plone.app.blob.tests',
           test_class=ReplacementFunctionalTestCase, optionflags=optionflags),
    ))


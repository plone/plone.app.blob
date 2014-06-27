import unittest
from plone.app.blob.tests.layer import BlobLayer, BlobReplacementLayer
from plone.app.blob.tests.layer import BlobLinguaLayer
try:
    # try to import the sample type for testing LinguaPlone
    from plone.app.blob.tests import lingua
    lingua      # make pyflakes happy...
except ImportError:
    pass




class BlobTestCase(unittest.TestCase):
    """ base class for integration tests """

    layer = BlobLayer


class BlobFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLayer


class ReplacementTestCase(unittest.TestCase):
    """ base class for integration tests using replacement types """

    layer = BlobReplacementLayer


class ReplacementFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobReplacementLayer


class BlobLinguaTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer


class BlobLinguaFunctionalTestCase(unittest.TestCase):
    """ base class for functional tests """

    layer = BlobLinguaLayer

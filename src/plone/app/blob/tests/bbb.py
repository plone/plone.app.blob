# helper module to ease setting up backward-compatibility tests for
# ATContentTypes and CMFPlone

from Testing.ZopeTestCase import installProduct
from plone.app.blob.tests import db     # set up a blob-aware zodb first
from plone.app.blob.tests.layer import BlobReplacementLayer

installProduct('GenericSetup', quiet=True)
installProduct('Marshall', quiet=True)

plone = BlobReplacementLayer
db  # make pyflakes happy...

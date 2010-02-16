import ZODB; ZODB   # make pyflakes happy...
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from plone.app.blob.tests.db import blobdirectory

print 'Setting up blob-aware ZODB storage ...'
Storage = BlobStorage(blobdirectory(), DemoStorage())

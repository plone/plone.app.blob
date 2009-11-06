import ZODB; ZODB   # make pyflakes happy...
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from tempfile import mkdtemp
from shutil import rmtree
from atexit import register

print 'Setting up blob-aware ZODB storage ...'
blobdir = mkdtemp()
register(rmtree, blobdir)
Storage = BlobStorage(blobdir, DemoStorage())

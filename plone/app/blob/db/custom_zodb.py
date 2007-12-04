import ZODB
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from tempfile import mkdtemp

print 'Setting up blob-aware ZODB storage ...'
Storage = BlobStorage(mkdtemp(), DemoStorage(quota=(1<<20)))

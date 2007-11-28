import ZODB
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from tempfile import mkdtemp

Storage = BlobStorage(mkdtemp(), DemoStorage(quota=(1<<20)))

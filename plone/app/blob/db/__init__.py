from os.path import dirname

import Testing
import App.config
cfg = App.config.getConfiguration()
cfg.testinghome = dirname(__file__)


# ZopeLite uses DemoStorage directly, so it needs monkey-patching... :(
from Testing.ZopeTestCase import ZopeLite
from ZODB.DemoStorage import DemoStorage
from ZODB.blob import BlobStorage
from tempfile import mkdtemp

def sandbox(base=None):
    """ returns a sandbox copy of the base ZODB """
    if base is None:
        base = ZopeLite.Zope2.DB
    base_storage = base._storage
    quota = getattr(base_storage, '_quota', None)
    storage = DemoStorage(base=base_storage, quota=quota)
    storage = BlobStorage(mkdtemp(), storage)
    return ZopeLite.ZODB.DB(storage)

ZopeLite.sandbox = sandbox

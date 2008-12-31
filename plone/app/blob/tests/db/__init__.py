from os.path import dirname

import Testing; Testing # make pyflakes happy...
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
    storage = DemoStorage(base=base._storage)
    storage = BlobStorage(mkdtemp(), storage)
    return ZopeLite.ZODB.DB(storage)

ZopeLite.sandbox = sandbox

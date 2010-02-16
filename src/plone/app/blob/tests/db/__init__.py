from ZODB.interfaces import IBlobStorage
from ZODB.DemoStorage import DemoStorage
from tempfile import mkdtemp
from shutil import rmtree
from atexit import register
from os.path import dirname


cache = {}
def blobdirectory():
    blobdir = cache.get('blobdir')
    if blobdir is None:
        blobdir = cache['blobdir'] = mkdtemp()
        register(rmtree, blobdir)
    return blobdir


# point the test setup to our private `custom_zodb.py`, but only if we
# have to, i.e. for plone 3.x
if not IBlobStorage.providedBy(DemoStorage()):
    import Testing; Testing # make pyflakes happy...
    import App.config
    cfg = App.config.getConfiguration()
    cfg.testinghome = dirname(__file__)


# ZopeLite uses DemoStorage directly, so it needs monkey-patching... :(
from Testing.ZopeTestCase import ZopeLite
from ZODB.blob import BlobStorage

def sandbox(base=None):
    """ returns a sandbox copy of the base ZODB """
    if base is None:
        base = ZopeLite.Zope2.DB
    storage = DemoStorage(base=base._storage)
    storage = BlobStorage(blobdirectory(), storage)
    return ZopeLite.ZODB.DB(storage)

if not IBlobStorage.providedBy(DemoStorage()):
    ZopeLite.sandbox = sandbox

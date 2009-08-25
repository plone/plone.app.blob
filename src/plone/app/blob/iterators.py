from zope.interface import implements
from zope.interface.interfaces import IInterface
from ZPublisher.Iterators import IStreamIterator
from os import fstat


class BlobStreamIterator(object):
    """ a streamiterator for blobs enabling to directly serve them
        in an extra ZServer thread """
    if IInterface.providedBy(IStreamIterator):  # is this zope 2.12?
        implements(IStreamIterator)
    else:
        __implements__ = (IStreamIterator,)

    def __init__(self, blob, mode='r', streamsize=1<<16):
        self.blob = blob.open(mode)
        self.streamsize = streamsize

    def next(self):
        data = self.blob.read(self.streamsize)
        if not data:
            raise StopIteration
        return data

    def __len__(self):
        return fstat(self.blob.fileno()).st_size

    def __iter__(self):
        return self

    # bbb methods to pretend we're a file-like object

    def close(self):
        return self.blob.close()

    def read(self, *args, **kw):
        return self.blob.read(*args, **kw)

    def seek(self, *args, **kw):
        return self.blob.seek(*args, **kw)

    def tell(self):
        return self.blob.tell()

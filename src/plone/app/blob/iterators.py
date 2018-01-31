# -*- coding: utf-8 -*-
from os import fstat
from plone.app.blob.utils import openBlob
from zope.interface import implementer
from ZPublisher.Iterators import IStreamIterator


@implementer(IStreamIterator)
class BlobStreamIterator(object):
    """ a streamiterator for blobs enabling to directly serve them
        in an extra ZServer thread """

    def __init__(self, blob, mode='r', streamsize=1 << 16, start=0, end=None):
        self.blob = openBlob(blob, mode)
        self.streamsize = streamsize
        self.start = start
        self.end = end
        self.seek(start, 0)

    def __next__(self):
        # Python 3
        """ return next chunk of data from the blob, taking the optionally
            given range into consideration """
        if self.end is None:
            bytes = self.streamsize
        else:
            bytes = max(min(self.end - self.tell(), self.streamsize), 0)
        data = self.blob.read(bytes)
        if not data:
            raise StopIteration
        return data

    next = __next__  # Python 2

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

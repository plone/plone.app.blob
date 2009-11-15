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


class BlobStreamRangeIterator(BlobStreamIterator):

    def __init__(self, blob, mode='r', streamsize=1<<16, start=0, end=None):
        self.blob = blob.open(mode)
        self.streamsize = streamsize
        self.start = start
        self.end = end
        self.seek(start, 0)

    def next(self):
        """
        raise a stopIteration if read bytes is upper than end value specified
        by the range validator
        """

        # this seems very ugly and it's not working
        # trying to set the end, cause we get a None from the downloadmanager
        if self.end is None:
            self.end = self.__len__()

        if self.tell() >= self.end:
            ## nothing to read
            raise StopIteration

        if self.tell() + self.streamsize > self.end:
            ## case of we must stop to the end buffer
            data = self.blob.read(self.end - self.tell())
            if not data:
                raise StopIteration
            return data

        else:
            ## normaly do the job like filestream_iterator
            data = self.blob.read(self.streamsize)
            if not data:
                raise StopIteration
            return data

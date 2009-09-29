# ZPublisher gets monkey-patched to use an extended version of the
# cgi module's FieldStorage class, so that temporary files used during
# file uploads are not anonymous, but instead provide a file name that
# can later be used with the blob class' `consumeFile` method...

from ZODB.blob import Blob
from ZPublisher import HTTPRequest
from tempfile import mkstemp, _TemporaryFileWrapper as TFW
from cgi import FieldStorage
from os.path import isfile
from os import unlink, fdopen


class TemporaryFileWrapper(TFW):
    """ variant of tempfile._TemporaryFileWrapper that doesn't rely on the
        automatic windows behaviour of deleting closed files, which even
        happens, when the file has been moved -- e.g. to the blob storage,
        and doesn't complain about such a move either """

    unlink = staticmethod(unlink)
    isfile = staticmethod(isfile)

    def close(self):
        if not self.close_called:
            self.close_called = True
            self.file.close()

    def __del__(self):
        self.close()
        if self.isfile(self.name):
            self.unlink(self.name)


class NamedFieldStorage(FieldStorage):

    def make_file(self, binary=None):
        handle, name = mkstemp()
        return TemporaryFileWrapper(fdopen(handle, 'w+b'), name)


original_init = HTTPRequest.FileUpload.__init__
def initFileUpload(self, aFieldStorage):
    original_init(self, aFieldStorage)
    file = aFieldStorage.file
    if not hasattr(file, '__methods__') and hasattr(file, 'name'):
        self.__dict__['name'] = file.name


HTTPRequest.FieldStorage = NamedFieldStorage
HTTPRequest.ZopeFieldStorage = NamedFieldStorage
HTTPRequest.FileUpload.__init__ = initFileUpload


# when CMFEditions creates a version, i.e. a copy of the to be versioned
# object, it creates a pickle of the object and then loads it again to
# construct a (deep) copy.  in the case of zodb blobs, this will also create
# new blob instances, but not copy the referenced blob files along the way.
# this might not be a problem in itself, as file and image content doesn't
# get versioned by default anyway, but the blob instance isn't properly
# initialized either (normally `__setstate__` would have been called at some
# point).
# to temporarily work around this wrappers are needed for some methods in
# `ZODB.blob.Blob`, with which folderish content containing blob-based files
# or images can be versioned without raising an error again.  please note
# though, that the contained files/images still won't.  once this has been
# properly fixed, the workaround can very likely be removed again...
#
# update: the methods in question have been fixed in zodb 3.8.1b8 and b9.
# as b9 hasn't been released yet the fix for `open` remains, but all of this
# should be removed once the new beta (or 3.8.1 final) is out.
def setstate_wrapper(method):
    def wrapper(self, *args, **kw):
        if self.readers is None and self.writers is None:
            self.__setstate__()     # set readers and writers to lists
        return method(self, *args, **kw)
    return wrapper

Blob.open = setstate_wrapper(Blob.open)


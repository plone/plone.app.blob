# ZPublisher gets monkey-patched to use an extended version of the
# cgi module's FieldStorage class, so that temporary files used during
# file uploads are not anonymous, but instead provide a file name that
# can later be used with the blob class' `consumeFile` method...

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

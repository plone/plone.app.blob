# ZPublisher gets monkey-patched to use an extended version of the
# cgi module's FieldStorage class, so that temporary files used during
# file uploads are not anonymous, but instead provide a file name that
# can later be used with the blob class' `consumeFile` method...

import os as _os

from ZPublisher import HTTPRequest
from tempfile import mkstemp, _TemporaryFileWrapper as TFWBase, _bin_openflags
from cgi import FieldStorage

class _TemporaryFileWrapper(TFWBase):
    """Variant of tempfile._TemporaryFileWrapper that doesn't rely on the
    automatic windows behaviour of deleting closed files, and doesn't
    complain if the file has been moved from under its feet"""

    unlink = staticmethod(_os.unlink)
    isfile = staticmethod(_os.path.isfile)
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
        fd, name = mkstemp()
        f = _os.fdopen(fd, "w+b", -1)
        return _TemporaryFileWrapper(f, name)


original_init = HTTPRequest.FileUpload.__init__
def initFileUpload(self, aFieldStorage):
    original_init(self, aFieldStorage)
    file = aFieldStorage.file
    if not hasattr(file, '__methods__') and hasattr(file, 'name'):
        self.__dict__['name'] = file.name


HTTPRequest.FieldStorage = NamedFieldStorage
HTTPRequest.FileUpload.__init__ = initFileUpload


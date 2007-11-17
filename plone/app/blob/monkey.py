# ZPublisher gets monkey-patched to use an extended version of the
# cgi module's FieldStorage class, so that temporary files used during
# file uploads are not anonymous, but instead provide a file name that
# can later be used with the blob class' `consumeFile` method...

from ZPublisher import HTTPRequest
from tempfile import NamedTemporaryFile
from cgi import FieldStorage


class NamedFieldStorage(FieldStorage):

    def make_file(self, binary=None):
        return NamedTemporaryFile("w+b")


original_init = HTTPRequest.FileUpload.__init__
def initFileUpload(self, aFieldStorage):
    original_init(self, aFieldStorage)
    file = aFieldStorage.file
    if not hasattr(file, '__methods__') and hasattr(file, 'name'):
        self.__dict__['name'] = file.name


HTTPRequest.FieldStorage = NamedFieldStorage
HTTPRequest.FileUpload.__init__ = initFileUpload


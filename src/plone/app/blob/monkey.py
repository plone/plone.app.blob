# -*- coding: utf-8 -*-
# XXX @gforcada: This got merged into Zope, will be available on
# Zope 4.0a2+.
# Merged by Hanno:
# https://github.com/zopefoundation/Zope/commit/4d5910f3130dbddd4
#
# ZPublisher gets monkey-patched to use an extended version of the
# cgi module's FieldStorage class, so that temporary files used during
# file uploads are not anonymous, but instead provide a file name that
# can later be used with the blob class' `consumeFile` method...

from cgi import FieldStorage
from os import fdopen
from os import unlink
from os.path import isfile
from tempfile import _TemporaryFileWrapper as TFW
from tempfile import mkstemp
from ZPublisher import HTTPRequest


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
    afile = aFieldStorage.file
    if not hasattr(afile, '__methods__') and hasattr(afile, 'name'):
        self.__dict__['name'] = afile.name


HTTPRequest.FieldStorage = NamedFieldStorage
HTTPRequest.ZopeFieldStorage = NamedFieldStorage
HTTPRequest.FileUpload.__init__ = initFileUpload

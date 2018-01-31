# -*- coding: utf-8 -*-
from os import name as os_name
from os.path import isfile
from plone.app.blob.field import ReuseBlob
from plone.app.blob.interfaces import IBlobbable
from plone.app.blob.interfaces import IFileUpload
from plone.app.blob.utils import guessMimetype
from shutil import copyfileobj
from ZODB.blob import Blob
from zope.component import adapter
from zope.interface import implementer


@adapter(IFileUpload)
@implementer(IBlobbable)
class BlobbableFileUpload(object):
    """ adapter for FileUpload objects to work with blobs """

    def __init__(self, context):
        self.context = context
        self.__mimetype = guessMimetype(self.context, self.filename())

    def feed(self, blob):
        """ see interface ... """
        cached = getattr(self.context, 'blob', None)
        if cached is not None and isinstance(cached, Blob):
            raise ReuseBlob(cached)
        else:
            self.context.blob = blob
        filename = getattr(self.context, 'name', None)
        if os_name == 'nt' and filename is not None:
            # for now a copy is needed on windows...
            with blob.open('w') as blobfile:
                copyfileobj(self.context, blobfile)
        elif filename is not None:
            assert isfile(filename), 'invalid file for blob: {0}'.format(filename)  # noqa
            blob.consumeFile(filename)
        else:  # the cgi module only creates a tempfile for 1000+ bytes
            self.context.seek(0)  # just to be sure we copy everything...
            with blob.open('w') as blobfile:
                blobfile.write(self.context.read())

    def filename(self):
        """ see interface ... """
        return self.context.filename

    def mimetype(self):
        """ see interface ... """
        return self.__mimetype

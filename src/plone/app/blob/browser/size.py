from Acquisition import aq_inner
from Products.Five import BrowserView
from time import strftime


def bytesize(size):
    if size.endswith('kB'):
        size = float(size[:-2]) * 1024
    elif size.endswith('MB'):
        size = float(size[:-2]) * 1024**2
    elif size.endswith('GB'):
        size = float(size[:-2]) * 1024**3
    else:
        size = float(size)
    return long(size)


class FileContentSizeView(BrowserView):

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write
        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg)
        return log

    def __call__(self, portal_type=['File', 'Image']):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        log = self.mklog()
        log('determining total size for content of type %r\n' % portal_type)
        log('please hang on, this might take a moment...\n')
        count = 0
        size = 0L
        brains = context.portal_catalog(portal_type=portal_type)
        for brain in brains:
            count += 1
            size += bytesize(brain.getObjSize)
            if count % 1000 == 0:
                log('%d/%d...\n' % (count, len(brains)))
        log('%d objects for a total size of %.2f MB (%d bytes)\n' % (count,
            float(size) / 1024**2, size))

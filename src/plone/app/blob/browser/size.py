# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


def bytesize(size):
    if size.endswith('kB'):
        size = float(size[:-2]) * 1024
    elif size.endswith('MB'):
        size = float(size[:-2]) * 1024 ** 2
    elif size.endswith('GB'):
        size = float(size[:-2]) * 1024 ** 3
    else:
        size = float(size)
    return long(size)


class FileContentSizeView(BrowserView):

    def __call__(self):
        context = aq_inner(self.context)
        query = dict(path='/'.join(context.getPhysicalPath()))
        query.update(self.request.form)
        if '-C' in query:
            del query['-C']
        write = self.request.RESPONSE.write

        def log(msg, *args):
            write(msg % args + '\n')
        log('Analysing content size (parameters %r)', query)
        log('Please hang on, this might take a moment...')
        counts = {}
        sizes = {}
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog.unrestrictedSearchResults(**query)
        log('Found %d results, counting...', len(brains))
        for idx, brain in enumerate(brains):
            pt = brain.portal_type
            counts[pt] = counts.setdefault(pt, 0) + 1
            sizes[pt] = sizes.setdefault(pt, 0) + bytesize(brain.getObjSize)
            if idx % 1000 == 0:
                log('%d/%d...', idx, len(brains))
        log('')
        fmt = '%-20s %6s items, %6.1f mb (%d bytes),\t%12.1f avg'
        comp = lambda a, b: cmp(b[1], a[1])
        for pt, size in sorted(sizes.items(), comp):
            count = counts[pt]
            size = float(size)
            log(fmt, pt + ':', count, size / 1024 ** 2, size, size / count)
        count = sum(counts.values())
        size = float(sum(sizes.values()))
        log(fmt, 'Totals', count, size / 1024 ** 2, size, size / count)

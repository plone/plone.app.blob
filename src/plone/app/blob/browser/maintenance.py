from logging import getLogger
from time import time, strftime
from transaction import commit
from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from plone.app.blob.interfaces import IATBlob
from plone.app.blob.markings import markAs


def timer(func=time):
    """ set up a generator returning the elapsed time since the last call """

    def gen(last=func()):
        while True:
            elapsed = func() - last
            last = func()
            yield '%.3fs' % elapsed
    return gen()


def checkpointIterator(function, interval=100):
    """ the iterator will call the given function for every nth invocation """
    counter = 0
    while True:
        counter += 1
        if counter % interval == 0:
            function()
        yield None


class MaintenanceView(BrowserView):
    """ helper view for upgrade & maintenance tasks """

    def mklog(self):
        """ helper to prepend a time stamp to the output """
        write = self.request.RESPONSE.write

        def log(msg, timestamp=True):
            if timestamp:
                msg = strftime('%Y/%m/%d-%H:%M:%S ') + msg
            write(msg)
        return log

    def resetSubtypes(self, batch=1000):
        """ walk all catalog entries and reset sub-type markings """
        log = self.mklog()
        log('resetting blob sub-type markers...\n')
        real = timer()          # real time
        lap = timer()           # real lap time (for intermediate commits)
        processed = 0

        def checkPoint():
            log('intermediate commit (%d items processed, '
                'last batch in %s)...\n' % (processed, lap.next()))
            commit()
        cpi = checkpointIterator(checkPoint, batch)
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        for brain in catalog(object_provides=IATBlob.__identifier__):
            obj = brain.getObject()
            subtype = brain.portal_type
            markAs(obj, subtype)
            obj.reindexObject(idxs=['object_provides'])
            log('set blob sub-type for %r to "%s"\n' % (obj, subtype))
            processed += 1
            cpi.next()
        commit()
        msg = 'processed %d items in %s.' % (processed, real.next())
        log(msg)
        getLogger('plone.app.blob.maintenance').info(msg)

    def updateTypeIndex(self, batch=1000):
        """ walk all catalog entries and update the 'Type' index """
        log = self.mklog()
        log('updating "Type" index for blob-based content...\n')
        real = timer()          # real time
        lap = timer()           # real lap time (for intermediate commits)
        processed = 0

        def checkPoint():
            log('intermediate commit (%d items processed, '
                'last batch in %s)...\n' % (processed, lap.next()))
            commit()
        cpi = checkpointIterator(checkPoint, batch)
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        for brain in catalog(object_provides=IATBlob.__identifier__):
            obj = brain.getObject()
            obj.reindexObject(idxs=['Type'])
            log('updated %r\n' % obj)
            processed += 1
            cpi.next()
        commit()
        msg = 'processed %d items in %s.' % (processed, real.next())
        log(msg)
        getLogger('plone.app.blob.maintenance').info(msg)

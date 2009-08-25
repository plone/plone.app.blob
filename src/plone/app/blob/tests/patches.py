from zope.interface.interfaces import IInterface
from ZPublisher.Iterators import IStreamIterator


def setBody(self, body, *args, **kw):
    if IInterface.providedBy(IStreamIterator):  # is this zope 2.12?
        stream = IStreamIterator.providedBy(body)
    else:
        stream = IStreamIterator.isImplementedBy(body)
    if stream:
        body = ''.join(body)    # read from iterator
    return self._original_setBody(body, *args, **kw)


def applyPatch(scope, original, replacement):
    setattr(scope, '_original_' + original, getattr(scope, original))
    setattr(scope, original, replacement)

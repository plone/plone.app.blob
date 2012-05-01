from zope.component import adapts

from Products.ATContentTypes.interface import IATNewsItem
from plone.app.blob.adapters.atimage import BlobbableATImage


class BlobbableATNewsItem(BlobbableATImage):
    """ adapter for ATNewsItem objects to work with blobs """
    adapts(IATNewsItem)

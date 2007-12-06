from Products.Five import BrowserView
from StringIO import StringIO

from plone.app.blob.migrations import migrateATFiles


class MigrationView(BrowserView):

    def migrateFiles(self):
        out = StringIO()
        print >> out, "starting ATFile migrations..."
        print >> out, migrateATFiles(self)
        return out.getvalue()


from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.blob.migrations import ATFileToBlobFileMigrator
from plone.app.blob.migrations import ATImageToBlobImageMigrator
from plone.app.blob.migrations import getATBlobFilesMigrationWalker
from plone.app.blob.migrations import getATBlobImagesMigrationWalker
from plone.app.blob.migrations import getATFilesMigrationWalker
from plone.app.blob.migrations import haveContentMigrations
from plone.app.blob.migrations import migrate
from plone.app.blob.migrations import migrateATBlobFiles
from plone.app.blob.migrations import migrateATBlobImages
from plone.app.blob.migrations import migrateATFiles

from Products.contentmigration.basemigrator.walker import Walker


class BlobMigrationView(BrowserView):

    migration = migrateATFiles
    walker = getATFilesMigrationWalker

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        options = {}
        clicked = request.form.has_key
        if not haveContentMigrations:
            msg = _(u'Please install contentmigrations to be able to migrate to blobs.')
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            options = { 'notinstalled': 42 }
        elif clicked('migrate'):
            output = self.migration()
            count = len(output.split('\n')) - 1
            msg = _(u'blob_migration_info',
                default=u'Blob migration performed for ${count} item(s).',
                mapping={'count': count})
            IStatusMessage(request).addStatusMessage(msg, type='info')
            options = { 'count': count, 'output': output }
        elif clicked('cancel'):
            msg = _(u'Blob migration cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(getToolByName(context, 'portal_url')())
        else:
            walker = self.walker()
            options = { 'available': len(list(walker.walk())) }
        return self.index(**options)


class FileMigrationView(BlobMigrationView):

    migration = migrateATBlobFiles
    walker = getATBlobFilesMigrationWalker


class ImageMigrationView(BlobMigrationView):

    migration = migrateATBlobImages
    walker = getATBlobImagesMigrationWalker


class SingleImageMigrationView(BrowserView):
    """Migrate just one piece of image"""

    def __call__(self):
        migrator = ATImageToBlobImageMigrator(self.context)
        migrator.migrate()
        return "Done"


class SingleFileMigrationView(BrowserView):
    """Migrate just one file"""

    def __call__(self):
        migrator = ATImageToBlobImageMigrator(self.context)
        migrator.migrate()
        return "Done"

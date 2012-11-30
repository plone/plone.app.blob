from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage

from plone.app.blob.migrations import haveContentMigrations
from plone.app.blob.migrations import migrateATFiles
from plone.app.blob.migrations import getATFilesMigrationWalker
from plone.app.blob.migrations import migrateATBlobFiles
from plone.app.blob.migrations import getATBlobFilesMigrationWalker
from plone.app.blob.migrations import migrateATBlobImages
from plone.app.blob.migrations import getATBlobImagesMigrationWalker
from plone.app.blob.migrations import migrateATBlobNewsItems
from plone.app.blob.migrations import getATBlobNewsItemsMigrationWalker


class BlobMigrationView(BrowserView):

    migration = migrateATFiles
    walker = getATFilesMigrationWalker

    def __call__(self):
        context = aq_inner(self.context)
        request = aq_inner(self.request)
        walker = self.walker()
        options = dict(target_type=walker.src_portal_type)
        clicked = request.form.has_key
        portal_url = getToolByName(context, 'portal_url')()
        ttool = getToolByName(context, 'portal_types')
        fti = ttool.get(walker.dst_portal_type)
        if fti and fti.product != 'plone.app.blob':
            url = '%s/prefs_install_products_form' % portal_url
            msg = _(u'Please install `plone.app.blob` to be able to migrate to blobs.')
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            options['notinstalled'] = 42
            options['installer'] = url
        elif not haveContentMigrations:
            msg = _(u'Please install contentmigrations to be able to migrate to blobs.')
            IStatusMessage(request).addStatusMessage(msg, type='warning')
            options['nomigrations'] = 42
        elif clicked('migrate'):
            output = self.migration()
            # Only count actual migration lines
            lines = output.split('\n')
            count = len([l for l in lines if l.startswith('Migrating')])
            msg = _(u'blob_migration_info',
                default=u'Blob migration performed for ${count} item(s).',
                mapping={'count': count})
            IStatusMessage(request).addStatusMessage(msg, type='info')
            options['count'] = count
            options['output'] = output
        elif clicked('cancel'):
            msg = _(u'Blob migration cancelled.')
            IStatusMessage(request).addStatusMessage(msg, type='info')
            request.RESPONSE.redirect(portal_url)
        else:
            options['available'] = len(list(walker.walk()))
        return self.index(**options)


class FileMigrationView(BlobMigrationView):

    migration = migrateATBlobFiles
    walker = getATBlobFilesMigrationWalker


class ImageMigrationView(BlobMigrationView):

    migration = migrateATBlobImages
    walker = getATBlobImagesMigrationWalker


class NewsItemMigrationView(BlobMigrationView):
    
    migration = migrateATBlobNewsItems
    walker = getATBlobNewsItemsMigrationWalker

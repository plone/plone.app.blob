try:
    from Products.contentmigration.archetypes import ATItemMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
    ATItemMigrator  # make pyflakes happy...
except ImportError:
    ATItemMigrator = object
    haveContentMigrations = False

from Products.CMFCore.utils import getToolByName
from transaction import savepoint


class ATFileToBlobMigrator(ATItemMigrator):
    src_portal_type = 'File'
    src_meta_type = 'ATFile'
    dst_portal_type = 'Blob'
    dst_meta_type = 'ATBlob'

    # migrate all fields except 'file', which needs special handling...
    fields_map = {
        'file': None,
    }

    def migrate_data(self):
        self.new.getField('file').getMutator(self.new)(self.old)

    def last_migrate_reindex(self):
        self.new.reindexObject()


def getATFilesMigrationWalker(self):
    """ set up walker for migrating ATFile instances """
    portal = getToolByName(self, 'portal_url').getPortalObject()
    return CustomQueryWalker(portal, ATFileToBlobMigrator, query = {})


def migrateATFiles(self):
    """ migrate ATFile instances """
    walker = getATFilesMigrationWalker(self)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


try:
    from Products.contentmigration.archetypes import ATItemMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
except ImportError:
    haveContentMigrations = False

from Products.CMFCore.utils import getToolByName
from transaction import savepoint


def migrateATFiles(self):
    """ migrate ATFile instances """

    if not haveContentMigrations:
        return 'WARNING: Please install contentmigrations to be able to migrate ATFiles.'

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

    portal = getToolByName(self, 'portal_url').getPortalObject()
    walker = CustomQueryWalker(portal, ATFileToBlobMigrator, query = {})
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


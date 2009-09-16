try:
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
    BaseMigrator = InplaceATItemMigrator
except ImportError:
    BaseMigrator = object
    haveContentMigrations = False

from Products.CMFCore.utils import getToolByName
from transaction import savepoint


def getMigrationWalker(context, migrator):
    """ set up migration walker using the given item migrator """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    return CustomQueryWalker(portal, migrator, use_savepoint=True)


def migrate(context, walker):
    """ migrate instances using the given walker """
    walker = walker(context)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


# migration of file content to blob content type
class ATFileToBlobMigrator(BaseMigrator):
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
        self.new.reindexObject(idxs=['object_provides', 'portal_type', 'UID'])


def getATFilesMigrationWalker(self):
    return getMigrationWalker(self, migrator=ATFileToBlobMigrator)

def migrateATFiles(self):
    return migrate(self, walker=getATFilesMigrationWalker)


# migration of file content to file replacement content type
class ATFileToBlobFileMigrator(ATFileToBlobMigrator):
    dst_portal_type = 'File'


def getATBlobFilesMigrationWalker(self):
    return getMigrationWalker(self, migrator=ATFileToBlobFileMigrator)

def migrateATBlobFiles(self):
    return migrate(self, walker=getATBlobFilesMigrationWalker)


# migration of image content to image replacement content type
class ATImageToBlobImageMigrator(ATFileToBlobMigrator):
    src_portal_type = 'Image'
    src_meta_type = 'ATImage'
    dst_portal_type = 'Image'
    dst_meta_type = 'ATBlob'

    # migrate all fields except 'image', which needs special handling...
    fields_map = {
        'image': None,
    }

    def migrate_data(self):
        self.new.getField('image').getMutator(self.new)(self.old)


def getATBlobImagesMigrationWalker(self):
    return getMigrationWalker(self, migrator=ATImageToBlobImageMigrator)

def migrateATBlobImages(self):
    return migrate(self, walker=getATBlobImagesMigrationWalker)


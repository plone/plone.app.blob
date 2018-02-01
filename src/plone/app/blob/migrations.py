# -*- coding: utf-8 -*-
try:
    from Products.contentmigration.archetypes import InplaceATItemMigrator
    from Products.contentmigration.migrator import BaseInlineMigrator
    from Products.contentmigration.walker import CustomQueryWalker
    haveContentMigrations = True
    BaseMigrator = InplaceATItemMigrator
    InlineMigrator = BaseInlineMigrator
except ImportError:
    BaseMigrator = object
    InlineMigrator = object
    haveContentMigrations = False

from Acquisition import aq_base
from plone.app.blob.field import BlobWrapper
from plone.app.blob.interfaces import IBlobField
from Products.Archetypes.interfaces import ISchema
from Products.CMFCore.utils import getToolByName
from transaction import savepoint


def getMigrationWalker(context, migrator):
    """ set up migration walker using the given item migrator """
    portal = getToolByName(context, 'portal_url').getPortalObject()
    return CustomQueryWalker(portal, migrator, use_savepoint=True)


def migrate(context, portal_type=None, meta_type=None, walker=None,
            remove_old_value=False):
    """ migrate instances using the given walker """
    if walker is None:
        migrator = makeMigrator(context, portal_type, meta_type,
                                remove_old_value,)
        walker = CustomQueryWalker(context, migrator, full_transaction=True)
    else:
        walker = walker(context)
    savepoint(optimistic=True)
    walker.go()
    return walker.getOutput()


# helper to build custom blob migrators for the given type
def makeMigrator(context, portal_type, meta_type=None, remove_old_value=False):
    """ generate a migrator for the given at-based portal type """
    if meta_type is None:
        meta_type = portal_type

    class BlobMigrator(InlineMigrator):
        """in-place migrator for archetypes based content that copies
        file/image data from old non-blob fields to new fields with the same
        name  provided by archetypes.schemaextender.

        see `plone3 to 4 migration guide`__

        .. __: http://docs.plone.org/4/en/manage/upgrading/version_specific_migration/p3x_to_p40_upgrade/index.html  #noqa
        """

        src_portal_type = portal_type
        src_meta_type = meta_type
        dst_portal_type = portal_type
        dst_meta_type = meta_type
        fields = []

        def getFields(self, obj):
            if not self.fields:
                # get the blob fields to migrate from the first object
                for field in ISchema(obj).fields():
                    if IBlobField.providedBy(field):
                        self.fields.append(field.getName())
            return self.fields

        @property
        def fields_map(self):
            fields = self.getFields(None)
            return dict([(name, None) for name in fields])

        def migrate_data(self):
            fields = self.getFields(self.obj)
            for name in fields:
                # access old field by not using schemaextender
                oldfield = self.obj.schema[name]
                is_imagefield = False
                if hasattr(oldfield, 'removeScales'):
                    # clean up old image scales
                    is_imagefield = True
                    oldfield.removeScales(self.obj)
                value = oldfield.get(self.obj)

                if not value:
                    # no image/file data: don't copy it over to blob field
                    # this way it's save to run migration multiple times w/o
                    # overwriting existing data
                    continue

                if isinstance(aq_base(value), BlobWrapper):
                    # already a blob field, no need to migrate it
                    continue

                # access new field via schemaextender
                field = self.obj.getField(name)
                field.getMutator(self.obj)(value)

                if remove_old_value:
                    # Remove data from old field to not end up with data
                    # stored twice - in ZODB and blobstorage
                    if is_imagefield:
                        oldfield.set(self.obj, 'DELETE_IMAGE')
                    else:
                        oldfield.set(self.obj, 'DELETE_FILE')

        def last_migrate_reindex(self):
            # prevent update of modification date during reindexing without
            # copying code from `CatalogMultiplex` (which should go anyway)
            od = self.obj.__dict__
            assert 'notifyModified' not in od
            od['notifyModified'] = lambda *args: None
            self.obj.reindexObject()
            del od['notifyModified']

    return BlobMigrator


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
        value = self.old.getField('file').getAccessor(self.old)()
        self.new.getField('file').getMutator(self.new)(value)

    def last_migrate_reindex(self):
        self.new.reindexObject(idxs=['object_provides', 'portal_type',
                                     'Type', 'UID'])


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
        value = self.old.getField('image').getAccessor(self.old)()
        self.new.getField('image').getMutator(self.new)(value)


def getATBlobImagesMigrationWalker(self):
    return getMigrationWalker(self, migrator=ATImageToBlobImageMigrator)


def migrateATBlobImages(self):
    return migrate(self, walker=getATBlobImagesMigrationWalker)

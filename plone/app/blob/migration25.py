from Products.ATContentTypes.migration.common import registerATCTMigrator
from Products.ATContentTypes.migration.walker import CatalogWalker
from Products.ATContentTypes.migration.migrator import CMFItemMigrator
from plone.app.blob.content import ATBlob


class FileMigrator(CMFItemMigrator):
    walkerClass = CatalogWalker

    def custom(self):
        ctype = self.old.getContentType()
        file = str(self.old)
        self.new.setFile(file, mimetype = ctype)


registerATCTMigrator(FileMigrator, ATBlob)


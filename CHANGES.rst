Changelog
=========

1.6.2 (2016-05-12)
------------------

Bug fixes:

- Blob images now reset EXIF data on save [martior]


1.6.1 (2015-11-26)
------------------

New:

- The blob file now gets exported when exporting content via
  GenericSetup.
  [do3cc]


1.6.0 (2015-09-21)
------------------

- Use configuration registry to set types_use_view_action_in_listings values.
  [esteele]


1.5.16 (2015-07-29)
-------------------

- Fix migrator for AT-based types that got broken in 1.5.8 release and add
  an option to remove the content of the non-blob field during migration to
  not end up having stale data in the ZODB
  [fRiSi]


1.5.15 (2015-05-31)
-------------------

- fix permission for download
  [david-batranu]


1.5.14 (2015-05-13)
-------------------

- fix tests for latest plone.app.imaging changes for Plone 5


1.5.13 (2015-05-05)
-------------------

- Fix tests from authenticator issues.
  [vangheem]


1.5.12 (2015-04-30)
-------------------

- Rerelease for clarity because of double release of 1.5.11.
  [maurits]


1.5.11 (2015-04-30)
-------------------

- Fix: Products.MimetypesRegistry used in p.a.blob.utils but no dependency
  [jensens]

- Fix some tests.
  [rafaelbco]

- ported tests to plone.app.testing
  [tomgross]


1.5.10 (2014-04-16)
-------------------

- Fix tests to work with barceloneta theme.
  [vangheem]


1.5.9 (2014-01-28)
------------------

- Make sure mimetype is not None and use use filename for detection if available.
  [tschanzt]

1.5.8 (2013-04-06)
------------------

- Use obj.Schema() instead of obj.schema in the migration process.
  [gbastien]


1.5.7 (2013-03-05)
------------------

- Only set the instance id from the name of an uploaded file
  if the file field is primary.
  [davisagli]


1.5.6 (2013-01-09)
------------------

- Fix BLOB migration when LinguaPlone is installed.
  Also for ATFile.

  CAUTION: when the fix was discussed with witsch,
  he pointed to the fact that the files would be
  entirely loaded in memory during migration.
  This could potentially eat too much memory.
  [gotcha]

- Don't fail on obscure chars in filename
  [tomgross]


1.5.5 (2012-11-29)
------------------

- Added adapter for data wrapped in xmlrpclib.Binary
  https://github.com/plone/plone.app.blob/pull/1
  [aclark, garbas]

- Fix BLOB migration when LinguaPlone is installed.
  [rpatterson]


1.5.4 (2012-10-15)
------------------

- Create a transaction savepoint after setting a blob's value in order to
  make it available at its temporary path (within the same transaction).
  [tomgross]


1.5.3 (2012-09-20)
------------------

- Update mutator to take care of filename in keyword args.
  [gotcha]

- Check for unicode filename first in ``index_html``.
  [vangheem]


1.5.2 (2012-05-25)
------------------

- Deprecated aliases were replaced on tests.
  [hvelarde]

- Keep the acquisition context of the blob in index_html, as otherwise
  we cannot get the http__etag method.
  [maurits]

- Move download implementation (the ``index_html`` method) to the blob
  wrapper class. The wrapper object is now directly viewable via the
  Zope 2 publisher.

  This change adds support for publishing of the original image data
  for any image field via the scaling view (even for fields that have
  been added via schema extension).

  Previously, if the blob wrapper was published for a content object
  that did not derive from the provided image class, Plone's default
  ``index_html`` template would be used, rendering an HTML page
  instead of the image.
  [malthe]


1.5.1 (2011-08-19)
------------------

- ATImage adapter should take care of cases where no image was uploaded.
  [gotcha]


1.5 (2011-04-21)
----------------

- Test fixes.
  [davisagli]


1.4 (2011-02-14)
----------------

- Avoid breaking on startup if PIL is not present.
  [davisagli]


1.3 (2010-09-28)
----------------

- Adjust tests to the fixed spelling of 'kB'.
  [witsch]


1.2 (2010-09-22)
----------------

- Fix the ``type`` of blob-based fields so they are distinguishable as
  blob fields.
  [davisagli]

- Fix broken migration-forms.
  [WouterVH]


1.1 (2010-08-13)
----------------

- Properly close written blobs in all `IBlobbable` adapters in order to
  avoid `POSKeyErrors`.
  This fixes http://plone.org/products/plone.app.blob/issues/43
  [jbaach, witsch]

- Allow explicitly setting a mimetype via a keyword passed to the mutator.
  [davidblewett, kleist, witsch]

- Don't raise `AttributeError` when calling `getSize` on empty images.
  [ggozad, witsch]


1.0 (2010-07-18)
----------------

- Correct blob migration count to ignore unrelated messages. This closes
  http://dev.plone.org/plone/ticket/10114.
  [hannosch]

- Update license to GPL version 2 only.
  [hannosch]


1.0b18 (2010-07-01)
-------------------

- Avoid deprecation warnings under Zope 2.13.
  [hannosch]

- Test fix: Use the API to look at request headers.
  [hannosch]


1.0b17 (2010-06-03)
-------------------

- Fix deletion of blob-based content even if the field is not called 'file'
  or 'image'.
  [regebro]

- The `ImageField` could not be copied, which broke the standard way of
  subclassing archetypes schemas.
  [regebro]

- Migration screen tried to check for installation via quick installer. We
  check the product of the destination portal type instead now. This closes
  http://dev.plone.org/plone/ticket/10365.
  [dunlapm, hannosch]

- Enable "Image" replacement content type by default.
  [witsch]

- Don't break when image-specific methods are accidentally used on
  "File" content.
  [witsch]


1.0b16 (2010-05-02)
-------------------

- Remove existing image scales when updating blob-aware image fields.
  Fixes http://dev.plone.org/plone/ticket/10455
  [frisi]

- Correct dependency on plone.app.imaging to >1.0b9 since we need the
  new IImageScaleFactory feature.
  [wichert]


1.0b15 (2010-04-10)
-------------------

- Provide blob-aware factory for new-style image scales.
  [witsch]

- Don't set the modification date of migrated content.
  [rossp]

- Restore support for defining per-field image scale sizes.
  Refs http://dev.plone.org/plone/ticket/10328 and
  fixes http://dev.plone.org/plone/ticket/10159
  [witsch]

- Provide base classes for file and image fields to be used in custom
  types not based on `archetypes.schemaextender`.
  Fixes http://dev.plone.org/plone/ticket/10328
  [witsch]

- Drop workaround for broken index accessor handling, which has been fixed
  upstream in `archetypes.schemaextender`.
  [witsch]

- Don't try to determine image dimensions for content other than images.
  Refs http://plone.org/products/cmfeditions/issues/58
  [witsch, do3cc]


1.0b14 (2010-03-07)
-------------------

- Revert the change to use the URL normalizer when generating content ids
  based on filename and reinstate the previous (and expected) behavior.
  Refs http://dev.plone.org/plone/ticket/8591
  [witsch]


1.0b13 (2010-03-06)
-------------------

- Use updated version of `createScales` as monkey-patched in
  `plone.app.imaging`.  Refs http://dev.plone.org/plone/ticket/10186
  [witsch]


1.0b12 (2010-02-16)
-------------------

- Change test setup to reuse the same directory when setting up blob
  storages, thereby fixing some BBB test issues.
  [witsch]

- Remove temporary monkey wrapper for `Blob.open` used to work around an
  issue with `CMFEditions`.  Refs http://dev.plone.org/plone/ticket/10200
  [witsch]

- Use URL normalizer when generating content ids based on filename.
  [terapyon, papago, witsch]

- Update view to analyse approximate content size grouped by type.
  [witsch]

- Add `z3c.autoinclude` entry point for automatic ZCML loading in Plone 3.3+.
  [witsch]

- Make sure image scales from old AT image fields are removed during
  migration to blob fields, when using the BlobMigrator.  This closes
  http://dev.plone.org/plone/ticket/10160
  [davisagli]

- Updated migration.pt to follow the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981
  [spliter]

- Make it possible to delete image content.
  [witsch]


1.0b11 (2010-01-30)
-------------------

- Fix issues regarding migration from `OFS.File` and `OFS.Image` content.
  [optilude, witsch]

- Revert changes to make things more robust in case of missing blob files.
  This refs http://plone.org/products/plone.app.blob/issues/10
  [witsch]

- Try to re-fetch blobs that have been removed from a client-side ZEO cache
  before giving up and raising an error.  This makes it possible to control
  the client blob cache size via external processes (e.g. `cron`) even with
  ZODB 3.8.  See http://dev.plone.org/plone/changeset/32170/ for more info.
  [svincic, witsch]

- Fix issue with incorrect values for "Type" catalog index after migration.
  [yomatters, witsch]


1.0b10 (2009-12-03)
-------------------

- Add support for accessing image scales via path expressions like
  `here/image_thumb` for backward-compatibility.
  [witsch]


1.0b9 (2009-11-26)
------------------

- Unify the ATBlob factories (for CMF>=2.2 and CMF<2.2) while still
  preventing events from being fired for the former.
  [witsch]

- Fix range support for open ranges.
  [j23d, witsch]

- Make the title field non-required for ATBlobs, since it will be
  generated from the filename if necessary.
  [davisagli]

- If a title was entered, use it instead of the filename to generate an
  id for files (matching what was already done for images).
  [davisagli]

- Update the CMF 2.2 version of the ATBlob factory to match a fix I made
  in Archetypes 2.0a2.
  [davisagli]


1.0b8 (2009-11-17)
------------------

- Added a modified version of the customized ATBlob factory for use with
  CMF 2.2.
  [davisagli]

- Make sure that BlobWrappers for zero-length blobs still evaluate to
  boolean True.
  [davisagli]

- Implement range support for downloads.  This fixes
  http://plone.org/products/plone.app.blob/issues/11
  [j23d, rossp, witsch]

- Fix image field validator to match that from `ATContentTypes`.
  [rossp]

- With `ATContentTypes` >=2.0, check the `_should_set_id_to_filename`
  method to determine if `ATBlob`'s `fixAutoId` method should set the
  item id to the filename of the blob field.  For images, don't set it
  to the filename if a title was supplied.
  [davisagli]

- Add blobbable adapters for Python file objects and OFS Pdata objects.
  [davisagli]

- Add helper view to get a rough estimate of the total size of binary
  content in a site.
  [witsch]


1.0b7 (2009-11-06)
------------------

- Fix regression in setup for running bbb tests against Plone 3.x.
  [witsch]

- Update migration view to issue warning when `plone.app.blob` has not
  been quick-installed yet.  Fixes http://dev.plone.org/plone/ticket/8496
  [witsch]

- Preserve filename when editing via WebDAV.  This fixes
  http://plone.org/products/plone.app.blob/issues/23
  [witsch]

- Update basic blob content type to be LinguaPlone-aware.  This fixes
  http://plone.org/products/plone.app.blob/issues/24
  [j23d]

- Override helper method to provide file-like objects for image
  transformations.  This fixes http://dev.plone.org/plone/ticket/8506
  [amleczko, witsch]

- Add some additional CMF/ATCT compatibility to the ATCT
  replacement types using the "cmf_edit" method.
  [alecm]

- Provide helper methods for easier migration of custom content types.
  [ggozad, witsch]

- Refactor test setup to make it work with ZODB 3.9.
  [witsch]


1.0b6 (2009-10-10)
------------------

- Minor fixes and test updates for compatibility with Plone 4.0.
  [witsch]

- Store image scales in blobs.
  [witsch]

- Use correct permissions when registering replacement types for
  "File" and "Image" content.
  See http://plone.org/products/plone.app.blob/issues/9
  [witsch]

- Fix migration issue regarding stale catalog index- & meta-data.
  [witsch]

- Allow certain file types to be downloaded immediately.
  See http://plone.org/products/plone.app.blob/issues/4
  [optilude]

- Fix performance issue regarding extension field.
  [witsch]


1.0b5 (2009-08-26)
------------------

- Fix compatibility issue with `repoze.zope2`.
  [optilude, witsch]

- Fix compatibility issues with ZODB 3.9 and Plone 4.0.
  [witsch]

- Speed up migration of existing content by using "in-place" migrators
  and avoid unnecessary re-indexing.
  [witsch]

- Fix registration of blob-based image scale adapter to prevent getting
  404s for content other than images.  This fixes the second issue
  related to http://plone.org/products/plone.app.blob/issues/19
  [witsch]


1.0b4 (2009-11-19)
------------------

- Provide maintenance view for (re)setting blob sub-types, which can also
  be used to fix things after upgrading from 1.0b2 or earlier.
  This fixes http://plone.org/products/plone.app.blob/issues/19
  [witsch]


1.0b3 (2009-11-15)
------------------

- Clean up GenericSetup profiles to allow separate installation of
  replacement types for "File" and "Image" content.
  [witsch]

- Add index accessor to make indexing of file content work again.
  This fixes http://plone.org/products/plone.app.blob/issues/12
  [witsch]

- Make code more robust in case of missing blob files.
  This fixes http://plone.org/products/plone.app.blob/issues/10
  [witsch]

- Make tests clean up their temporary blob directories.
  [stefan]

- Remove quota argument from DemoStorage calls.
  [stefan]

- Add workaround to prevent breakage with CMFEditions (blob-based
  content can still not be versioned, though).
  [witsch]

- Add missing acquisition-wrapper, also allowing to remove circular
  references between instance and field, which broke pickling.
  [witsch]

- Fix helper for determining image sizes to not break for non-image
  content.
  [witsch]

- Use PIL for determining image sizes as the OFS code cannot handle
  certain types of JPEGs.
  [witsch]

- Added missing metadata.xml to the default profile.
  [hannosch]

- Only use the file name for id generation for the replacement types,
  i.e. "File" and "Image", but not custom types.  This fixes
  http://plone.org/products/plone.app.blob/issues/3
  [witsch]

- Fix issue where the mime-type registry returned an empty tuple when
  looking up an unknown mime-type.  This fixes
  http://plone.org/products/plone.app.blob/issues/1
  [witsch]


1.0b2 (2008-02-29)
------------------

- Reverted fix for Windows that closed the file upload object in order
  to work around a problem with reading from the blob file afterwards.
  [witsch]


1.0b1 (2008-02-28)
------------------

- Minor bug fixes and cleanups
  [witsch]

- Fix for a problem regarding file uploads on Windows, where renaming
  the still open temporary file isn't allowed and hence caused an error.
  Now the file is closed before the call to `consumeFile()`.
  [rochael]

- Fix for Windows regarding the generation of the temporary file used for
  file uploads so that it doesn't get deleted after being moved to the
  blob storare
  [rochael]

- Change file size calculation so as not to need to reopen the file, which
  broke on Windows
  [rochael]

- Changed the primary field of the blob content types to not to be
  "searchable" as this causes indexing of the blob content making ram
  consumption go through the roof
  [witsch]


1.0a2 (2007-12-12)
------------------

- Various minor bug fixes regarding migration, content icons etc
  [witsch]

- String value are now wrapped using StringIO to make them adaptable, so
  that their mime-type can be guessed as well.
  [naro]

- Added alternative GenericSetup profile to allow to replace ATFile
  as the "File" content type
  [witsch]


1.0a1 (2007-12-07)
------------------

- Initial version
  [witsch]

- Initial package structure.
  [zopeskel]

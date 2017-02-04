Detailed Documentation
======================

This package integrates ZODB 3.8's blob support into Plone 3.0.  To do this a
new content type `Blob` is provided, which can be used instead of the existing
`File` and `Image` types.  Their behaviour is mimicked by `sub-typing`_, which
in this case means dynamically changing views and schema of the underlying
`Blob` type as well as adapting it to add functionality.

  .. _`sub-typing`: http://www.serverzen.com/training/subtyping-unleashed

First of all the `plone.app.blob` package needs to be installed, which at the
moment requires a special `branch`_ of Zope 2.10 as well as a few additional
packages for `extending the schema`_ and `migration purposes`_.  The easiest
way to get a working setup is probably to use one of the provided `buildout`_
configurations, either one `based on ploneout`_ and therefore mainly targeted
at developers or another `based on plone.recipe.plone`_.  The latter uses the
current plone release tarball instead of subversion checkout, meaning it is
mainly targeted at integrators and users (and significantly faster to set up
as well :)).

  .. _`branch`: http://svn.zope.org/Zope/branches/2.10-with-ZODB3.8/
  .. _`extending the schema`: http://dev.plone.org/archetypes/browser/archetypes.schemaextender/
  .. _`migration purposes`: http://dev.plone.org/collective/browser/contentmigration/
  .. _`buildout`: http://pypi.python.org/pypi/zc.buildout
  .. _`based on ploneout`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/ploneout
  .. _`based on plone.recipe.plone`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/plone-3.x

In any way, the setup should make the new content type available as well as
instantiable:

  >>> from Products.CMFCore.utils import getToolByName
  >>> portal = layer['portal']
  >>> portal_types = getToolByName(portal, 'portal_types')
  >>> portal_types.getTypeInfo('Blob')
  <DynamicViewTypeInformation at /plone/portal_types/Blob>

  >>> from plone.app.testing import TEST_USER_ID
  >>> folder = portal.portal_membership.getHomeFolder(TEST_USER_ID)
  >>> folder.invokeFactory('Blob', id='blob', title='a Blob')
  'blob'
  >>> blob = folder.blob
  >>> blob
  <ATBlob at /plone/Members/test_user_1_/blob>

The new instance should have been marked with the default sub-type and
therefore also contain the extended schema:

  >>> from plone.app.blob.interfaces import IATBlobBlob
  >>> IATBlobBlob.providedBy(blob)
  True
  >>> blob.getField('file')
  <Field file(blob:rw)>

Mimicking the existing "File" content type, i.e. `ATFile`, it shouldn't have
an associated workflow:

  >>> workflow_tool = getToolByName(portal, 'portal_workflow')
  >>> workflow_tool.getWorkflowsFor(blob)
  []

Since no data has been written to it, the blob file should still be empty:

  >>> blob.getFile().getBlob()
  <ZODB.blob.Blob object at ...>
  >>> blob.getFile().getBlob().open().read()
  ''

Feeding it with some image data should result in a correctly set mime-type
and a now non-empty blob file:

  >>> from StringIO import StringIO
  >>> from base64 import decodestring
  >>> gif = 'R0lGODlhAQABAPAAAPj8+AAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
  >>> gif = StringIO(decodestring(gif))
  >>> blob.setFile(gif)
  >>> print blob.getFilename()
  None
  >>> blob.getContentType()
  'image/gif'
  >>> len(blob.getFile().getBlob().open().read())
  43
  >>> str(blob) == gif.getvalue()
  True

Migration from existing file content, i.e. `ATFile` instances, is also
provided.  The payload data as well as all other fields should be properly
migrated:

  >>> initial_file_product = portal.portal_types.File.product
  >>> initial_file_factory = portal.portal_types.File.factory
  >>> portal.portal_types.File.product = 'ATContentTypes'
  >>> portal.portal_types.File.factory = 'addATFile'
  >>> gif.filename = 'foo.gif'
  >>> folder.invokeFactory('File', id='foo', title='a file', file=gif,
  ...     subject=('foo', 'bar'), contributors=('me'))
  'foo'
  >>> portal.portal_types.File.product = initial_file_product
  >>> portal.portal_types.File.factory = initial_file_factory
  >>> folder.foo
  <ATFile at /plone/Members/test_user_1_/foo>
  >>> folder.foo.Title()
  'a file'
  >>> folder.foo.getFilename()
  'foo.gif'
  >>> folder.foo.getContentType()
  'image/gif'
  >>> folder.foo.Subject()
  ('foo', 'bar')
  >>> folder.foo.Contributors()
  ('me',)

  >>> from plone.app.blob.migrations import migrateATFiles
  >>> migrateATFiles(portal)
  'Migrating /plone/Members/test_user_1_/foo (File -> Blob)\n'

  >>> folder.foo
  <ATBlob at /plone/Members/test_user_1_/foo>
  >>> folder.foo.Title()
  'a file'
  >>> folder.foo.getFilename()
  'foo.gif'
  >>> folder.foo.getContentType()
  'image/gif'
  >>> folder.foo.Subject()
  ('foo', 'bar')
  >>> folder.foo.Contributors()
  ('me',)
  >>> folder.foo.getFile().getBlob()
  <ZODB.blob.Blob object at ...>
  >>> str(folder.foo) == gif.getvalue()
  True
  >>> folder.foo.getFile().getBlob().open().read()
  'GIF89a...'

Also, migrating should have indexed the new content correctly to prevent stale
or wrong data from showing up in some views, i.e. folder listing:

  >>> catalog = getToolByName(portal, 'portal_catalog')
  >>> brain = catalog(id = 'foo')[0]
  >>> folder.foo.UID() == brain.UID
  True

  >>> folder.foo.getObjSize() == brain.getObjSize
  True

Finally the correct creation of blob-based content "through the web" is tested
using a testbrowser:

  >>> from plone.app.testing import setRoles
  >>> setRoles(portal, TEST_USER_ID, ['Editor'])

  >>> from plone.testing.z2 import Browser

  >>> from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
  >>> browser = Browser(layer['app'])
  >>> browser.addHeader('Authorization', 'Basic %s:%s' % (
  ...     TEST_USER_NAME, TEST_USER_PASSWORD))

  >>> browser.open(folder.absolute_url())
  >>> browser.getLink(url='createObject?type_name=Blob').click()
  >>> browser.url
  'http://nohost/plone/.../portal_factory/Blob/blob.../edit...'
  >>> browser.getControl(name='title').value = 'Foo bar'
  >>> control = browser.getControl(name='file_file')
  >>> testfile = StringIO('%PDF-1.4 fake pdf...' + 'foo' * 1000)
  >>> control.add_file(testfile, None, 'foo.pdf')
  >>> browser.getControl('Save').click()
  >>> browser.url
  'http://nohost/plone/.../foo-bar/view'
  >>> browser.contents
  '...Info...Changes saved...
   ...Foo bar...foo.pdf...PDF document...'


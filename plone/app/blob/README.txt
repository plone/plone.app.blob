==============
plone.app.blob
==============

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
  .. _`based on plone.recipe.plone`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/plone-3.0

In any way, the setup should make the new content type available as well as
instantiable:

  >>> from Products.CMFCore.utils import getToolByName
  >>> portal_types = getToolByName(portal, 'portal_types')
  >>> portal_types.getTypeInfo('Blob')
  <DynamicViewTypeInformation at /plone/portal_types/Blob>

  >>> folder.invokeFactory('Blob', id='blob', title='a Blob')
  'blob'
  >>> folder.blob
  <ATBlob at /plone/Members/test_user_1_/blob>


==============
plone.app.blob
==============

Overview
========

This package aims to be an add-on for Plone (>= 3.x) integrating ZODB (>=3.8)
blob support, which allows large binary data to be managed by the ZODB, but
separately from your usual ``FileStorage`` database, i.e. ``Data.fs``.  This
has several advantages, most importantly a much smaller ``Data.fs`` and better
performance both cpu- as well as memory-wise.

  .. |__| unicode:: U+20  .. space


Contents
========

.. contents:: |__|


Status
======

At the moment the integration for "File" content should be stable, but still
needs more field testing.  It is being successfully used in several production
deployments, though.  The provided blob-based content type should safely
usable as a drop-in replacement for ``ATFile``.  As such it has been
successfully tested against all ``CMFPlone`` and ``ATContentTypes`` tests.
Please use the provided ``test-compatibility.sh`` script to run these tests
for yourself.

Image support is still in an alpha stadium and not enabled by default. It can
be activated by applying the respective profile via the portal setup tool.

More detailed information about the integration and the current status can be
found in the corresponding `Plone enhancement`_ and `Plone 4 PLIP`_ tickets.

  .. _`Plone enhancement`: http://dev.plone.org/plone/ticket/6805
  .. _`Plone 4 PLIP`: http://dev.plone.org/plone/ticket/7822
  .. |--| unicode:: U+2013   .. en dash
  .. |---| unicode:: U+2014  .. em dash


Requirements
============

Plone 3.0 or newer is required. The package has been tested with all versions
from 3.0 up to and including 4.0. However, as all versions before 3.0.4
require a workaround described in the `Troubleshooting`_ section below, it is
recommended to use `Plone 3.0.4`_ or a more recent version.

  .. _`Plone 3.0.4`: http://plone.org/products/plone/releases/3.0.4


Installation
============

The easiest way to get ZODB blob support in Plone 3 using this package is to
work with installations based on `zc.buildout`_.  Other types of installations
should also be possible, but might turn out to be somewhat tricky |---| please
see the `FAQ`_ section below.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"plone.app.blob" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

A sample buildout configuration file, i.e. ``buildout.cfg``, could look like
this::

  [buildout]
  parts = zope2 instance
  extends = http://dist.plone.org/release/3.3.1/versions.cfg
  find-links =
      http://dist.plone.org/release/3.3.1
      http://dist.plone.org/thirdparty/
  versions = versions

  [versions]
  ZODB3 = 3.8.3

  [zope2]
  recipe = plone.recipe.zope2install
  url = ${versions:zope2-url}

  [instance]
  recipe = plone.recipe.zope2instance
  zope2-location = ${zope2:location}
  blob-storage = var/blobstorage
  user = admin:admin
  eggs =
      Plone
      plone.app.blob
  zcml = plone.app.blob

You can also use this buildout configuration to create a fresh Plone
installation. To do so you would store it as ``buildout.cfg`` |---| preferably
in an empty directory, download `bootstrap.py
<http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py>`_
into the same directory and issue the following commands::

  $ python bootstrap.py
  $ ./bin/buildout
  $ ./bin/instance fg

After that you create a "Plone Site" via the `ZMI`_ as usual and either
select the "plone.app.blob" extension profile at creation time or again
install the "plone.app.blob" package using one of the above mentioned methods.

  .. _`ZMI`: http://localhost:8080/manage

A sample ZEO buildout configuration could look like this::

  [buildout]
  parts = zope2 zeoserver instance1 instance2
  extends = http://dist.plone.org/release/3.3.1/versions.cfg
  find-links =
      http://dist.plone.org/release/3.3.1
      http://dist.plone.org/thirdparty/
  versions = versions

  [versions]
  ZODB3 = 3.8.3

  [zope2]
  recipe = plone.recipe.zope2install
  url = ${versions:zope2-url}

  [zeoserver]
  recipe = plone.recipe.zope2zeoserver
  zope2-location = ${zope2:location}
  zeo-address = 127.0.0.1:8100
  zeo-var = ${buildout:directory}/var
  blob-storage = ${zeoserver:zeo-var}/blobstorage
  eggs = plone.app.blob

  [instance1]
  recipe = plone.recipe.zope2instance
  zope2-location = ${zope2:location}
  zeo-address = ${zeoserver:zeo-address}
  blob-storage = ${zeoserver:blob-storage}
  zeo-client = on
  shared-blob = on
  user = admin:admin
  eggs =
      Plone
      plone.app.blob
  zcml = plone.app.blob

  [instance2]
  recipe = plone.recipe.zope2instance
  http-address = 8081
  zope2-location = ${instance1:zope2-location}
  zeo-client = ${instance1:zeo-client}
  zeo-address = ${instance1:zeo-address}
  blob-storage = ${instance1:blob-storage}
  shared-blob = ${instance1:shared-blob}
  user = ${instance1:user}
  eggs = ${instance1:eggs}
  zcml = ${instance1:zcml}

Please note the configuration options ``blob-storage`` and ``shared-blob``
specified in ``[client1]`` and ``[client2]``.  To enable blob support on a ZEO
client (or standalone instance) you always have to specify a path in the
``blob-storage`` configuration option.  If ``shared-blob`` is set to "on", the
ZEO client will assume it can read blob files directly from within the path
specified in the ``blob-storage`` option.  This path might also refer to a
network share in case the ZEO client and server are installed on separate
machines. However, to stream blob files trough the ZEO connection you will
have to set the ``shared-blob`` option to "off".  The path specified in the
``blob-storage`` option will be ignored in this situation, but it needs to be
set nevertheless.

More detailed instructions on how to set things up as well as some background
information on blobs |---| or in other words the story of an "early adopter"
|---| can be found in `Ken Manheimer's wiki`__.  This is a highly useful
resource and recommended read for people trying to give blobs a spin.  Please
note however, that most of the recipe changes described in these instructions
have already been incorporated in the particular recipes by now.

  .. __: http://myriadicity.net/Sundry/PloneBlobs

In addition, more information on how to use buildout is available in the
`accompanying README.txt`__ as well as in `Martin's`_ excellent `buildout
tutorial`_ on `plone.org`_.

  .. __: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.x/README.txt
  .. _`Martin's`: http://martinaspeli.net/
  .. _`buildout tutorial`: http://plone.org/documentation/tutorial/buildout
  .. _`plone.org`: http://plone.org/


Migrating existing content
==========================

In-place content migration is provided for existing "File" and "Image"
content.  The `Products.contentmigration`_ package is required for this to
work.  To install this package you will again need to add its name to the
"eggs" and "zcml" section of your ``buildout.cfg``, so that it reads like::

  [instance]
  ...
  eggs +=
      plone.app.blob
      Products.contentmigration
  zcml +=
      plone.app.blob
      Products.contentmigration

You can also refer to the above mentioned `sample buildout.cfg`_ for details.

  .. _`Products.contentmigration`: http://pypi.python.org/pypi/Products.contentmigration/
  .. _`sample buildout.cfg`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/plone-3.x/buildout.cfg

In order to then migrate your existing file content to blobs you can use the
migration interfaces provided at ``http://<site>/@@blob-file-migration`` to
migrate "File" content as well as ``http://<site>/@@blob-image-migration``
for "Image" content respectively.  ``<site>`` will need to be replaced with
the URL of your "Plone Site" object here, of course.  The pages will show you
the number of available ``ATFile`` or ``ATImage`` instances and then lets you
convert these to the provided blob content types by clicking a button.

For custom AT-based content types that use FileField(s), see
`example.blobattype`_ for details of how to enable and migrate them to use
blobs.

  .. _`example.blobattype`: http://pypi.python.org/pypi/example.blobattype

Please refer to the next section if you encounter any errors during migration.


Troubleshooting
===============

The following are some known issues, that will hopefully be resolved soon
enough.  In the meantime here are the recommended workarounds:


**"AttributeError: 'module' object has no attribute 'VersionBase'" Exception**

  Symptom
    After upgrading your buildout you're getting errors like the following::

      Traceback (innermost last):
        ...
        Module App.PersistentExtra, line 57, in locked_in_version
      AttributeError: 'module' object has no attribute 'VersionBase'
  Problem
    Version `1.0b5`_ of ``plone.app.blob`` adds `support for Plone 4`_ as
    well as `Dexterity`_, which is why the version restriction for ZODB had
    to be lifted.  However, while Plone 4 will use Zope 2.12 and ZODB 3.9,
    Plone 3.x doesn't work with either of these.
  Solution
    Downgrade ``ZODB3`` to a release from the 3.8 series.  You can do this by
    adding a version pin like::

      [versions]
      ZODB3 = 3.8.3

    to your ``buildout.cfg``.

  .. _`1.0b5`: http://pypi.python.org/pypi/plone.app.blob/1.0b5
  .. _`support for Plone 4`: http://dev.plone.org/plone/ticket/7822
  .. _`Dexterity`: http://plone.org/products/dexterity/


**"FileFieldException: Value is not File or String (...)" Exception**

  Symptom
    After upgrading your buildout you're getting an error like the following
    during blob migration::

      Traceback (innermost last):
        File ".../basemigrator/walker.py", line 174, in migrate
        ...
        File ".../Archetypes/Field.py", line 931, in _process_input
      FileFieldException: Value is not File or String (...)
  Problem
    Your version of ``archetypes.schemaextender`` has been upgraded to `1.1`_
    while running buildout.  You either didn't run it in non-newest mode
    (``-N``) or have not pinned down the version of
    ``archetypes.schemaextender``.
  Solution
    Downgrade ``archetypes.schemaextender`` to version 1.0 for the moment.
    You can do this by adding a version pin like::

      [versions]
      archetypes.schemaextender = 1.0

    to your ``buildout.cfg``.  A proper fix to add compatibility to the
    latest version is being worked on.

  .. _`1.1`: http://pypi.python.org/pypi/archetypes.schemaextender/1.1


**"AttributeError: 'NoneType' object has no attribute 'getAccessor'" Exception**

  Symptom
    After upgrading from version `1.0b2`_ or earlier you're getting an error
    like the following when trying to view blob-based content::

      Traceback (innermost last):
        Module ZPublisher.Publish, line 119, in publish
        ...
        Module Products.ATContentTypes.content.base, line 300, in get_content_type
      AttributeError: 'NoneType' object has no attribute 'getAccessor'
  Problem
    Recent versions have added support for sub-types based on marker
    interfaces and your existing blob-based content hasn't been marked yet.
  Solution
    Upgrade to at least `1.0b4`_, re-install "plone.app.blob" via the
    quick-installer and reset all sub-types by accessing the
    ``@@blob-maintenance/resetSubtypes`` view.

  .. _`1.0b2`: http://pypi.python.org/pypi/plone.app.blob/1.0b2
  .. _`1.0b4`: http://pypi.python.org/pypi/plone.app.blob/1.0b4


**"Invalid plugin id" Exception**

  Symptom
    When trying to create a "Plone Site" you're getting an error like::

      Error Type: KeyError
      Error Value: 'Invalid plugin id: credentials_basic_auth'
  Problem
    Your version of ``Products.PluggableAuthService`` is too old |---| you need
    1.5.2 or newer (please see http://www.zope.org/Collectors/PAS/59 for more
    information about this).
  Solution
    Please use the `provided buildout`_, add the `1.5 branch`_ as an
    `svn:external`_ to the ``products/`` directory of your buildout or
    upgrade to `Plone 3.0.4`_ by re-running buildout.

  .. _`provided buildout`: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.x
  .. _`1.5 branch`: http://svn.zope.org/Products.PluggableAuthService/branches/1.5/
  .. _`svn:external`: http://svnbook.red-bean.com/en/1.0/ch07s03.html


**"unknown type name: 'blobstorage'"**

  Symptom
    When running buildout you're getting an error like::

      Error: unknown type name: 'blobstorage'
      (line 36 in file:///.../parts/instance/etc/zope.conf)
  Problem
    Your version of the `plone.recipe.zope2instance`_ recipe is too old
    |---| you need to have at least version `1.0`_.
  Solution
    Make sure you're running buildout with neither "``-N``" nor "``-o``" and
    you also don't have::

      newest = false

    in your ``~/.buildout/default.cfg``.  Alternatively, running buildout
    with option "``-n``" should update the recipe to the latest version.

  .. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance/
  .. _`1.0`: http://pypi.python.org/pypi/plone.recipe.zope2instance/1.0


**missing distribution for required "zdaemon" and "ZConfig" eggs**

  Symptom
    When running buildout you're getting errors like::

      Getting distribution for 'zdaemon>=1.4a2,<1.4.999'.
      While:
        Installing instance.
        Getting distribution for 'zdaemon>=1.4a2,<1.4.999'.
      Error: Couldn't find a distribution for 'zdaemon>=1.4a2,<1.4.999'.

    or::

      Getting distribution for 'ZConfig>=2.4a2,<2.4.999'.
      While:
        Installing instance.
        Getting distribution for 'ZConfig>=2.4a2,<2.4.999'.
      Error: Couldn't find a distribution for 'ZConfig>=2.4a2,<2.4.999'.
  Problem
    ``zdaemon`` and ``ZConfig`` eggs have only been released to the
    `Cheeseshop`_ starting from more recent versions, i.e. 2.0 and 2.5
    respectively.  Older distributions in egg format are only available
    from http://download.zope.org/distribution
  Solution
    Add the above link to the ``find-links`` setting of the ``[buildout]``
    section in your ``buildout.cfg``, like::

      find-links =
          http://download.zope.org/distribution/
          ...

  .. _`Cheeseshop`: http://pypi.python.org/pypi


**"ZRPCError: bad handshake 'Z303'"**

  Symptom
    With a ZEO setup you are getting errors like::

      ZRPCError: bad handshake 'Z303'
  Problem
    You probably haven't added ``plone.app.blob`` to the ``eggs`` setting in
    your ``[zeo]`` buildout part.  Without it the ZEO server will not use
    the required version 3.8 of ZODB and hence not support blobs.
  Solution
    Add the string ``plone.app.blob`` to the ``eggs`` setting in the ``[zeo]``
    section (i.e. the one using the ``plone.recipe.zope2zeoserver`` recipe)
    in your ``buildout.cfg``, like::

      [zeo]
      ...
      eggs = plone.app.blob
      ...


**"AttributeError: 'NoneType' object has no attribute 'product'" during migration**

  Symptom
    After installing "plone.app.blob" via the quick-installer or applying
    the "plone.app.blob: ATFile replacement" profile you are seeing migration
    errors like::

      Traceback (innermost last):
        Module ZPublisher.Publish, line 119, in publish
        Module ZPublisher.mapply, line 88, in mapply
        Module ZPublisher.Publish, line 42, in call_object
        Module plone.app.blob.browser.migration, line 24, in __call__
        Module plone.app.blob.migrations, line 42, in migrateATFiles
        Module Products.contentmigration.basemigrator.walker, line 126, in go
        Module Products.contentmigration.basemigrator.walker, line 205, in migrate
      MigrationError: MigrationError for obj at /... (File -> Blob):
      Traceback (most recent call last):
        File ".../Products/contentmigration/basemigrator/walker.py", line 174, in migrate
          migrator.migrate()
        File ".../Products/contentmigration/basemigrator/migrator.py", line 185, in migrate
          method()
        File ".../Products/contentmigration/archetypes.py", line 111, in beforeChange_schema
          archetype = getType(self.dst_meta_type, fti.product)
      AttributeError: 'NoneType' object has no attribute 'product'
  Problem
    The current migration code has been written to convert existing "File"
    content to the "Blob" content type provided by the base "plone.app.blob"
    profile.  However, that type isn't known when just installing the "ATFile
    replacement" profile.  The latter is probably what you want to install,
    though, as former "File" content will keep the same portal type, i.e.
    "File" after being migrated.  This way no apparent changes are visible,
    which might help with avoiding confusion.
  Solution
    For now you might work around this by either applying the "plone.app.blob"
    profile via the ZMI in ``/portal_setup``.  This will install the above
    mentioned "Blob" content type.  After that migration will work, but your
    former "File" content will have the "Blob" content type.

    If that's not what you want, simply change line line 17 in
    ``plone/app/blob/migrations.py`` (which is probably contained in an egg
    directory located somewhere like ``eggs/plone.app.blob-1.0b2-py2.4.egg/``
    relative to your buildout/installation) from::

       dst_portal_type = 'Blob'

    to::

       dst_portal_type = 'File'

    After that migration should use the new "File" type, based on ZODB blobs.
    Once you've migrated you might remove or disable the "Blob" type from
    ``/portal_types`` again.  A future version of "plone.app.blob" will try
    auto-detect the correct target type for the migration (or at least allow
    to specify it) to make this more convenient.

    If you have already migrated to "Blob" content, but would rather like to
    have "File" items, you can change the two previous lines to::

       src_portal_type = 'Blob'
       src_meta_type = 'ATBlob'

    and re-run the blob migration.  This will convert your "Blob"s to show up
    as "File"s again.  You should probably pack your ZODB afterwards to avoid
    having its blob storage occupy twice as much disk space as actually
    needed (the extra migration will create new blobs).


**"Image" and/or "File" content doesn't show up as expected after migrating to blobs**

  Symptom
    After migrating "Image" and/or "File" content to be based on blobs, some
    of it doesn't show up as expected.  A typical example of this are ATCT's
    photo album views.
  Problem
    All versions before 1.0b11 didn't update the "Type" catalog index
    correctly during migration.  This could of course result in wrong results
    for all queries using this index.
  Solution
    Manually update the "Type" index using the ZMI or upgrade to at least
    `1.0b11`_ and use the ``@@blob-maintenance/updateTypeIndex`` view to
    limit the reindexing to only blob-based content.  The latter should
    usually be quicker, especially for bigger sites.

  .. _`1.0b11`: http://pypi.python.org/pypi/plone.app.blob/1.0b11


**Errors when using additionally mounted databases**

  Symptom
    With additionally configured ZODB mount-points you are getting errors
    like::

      Traceback (innermost last):
        ...
        Module ZEO.ClientStorage, line 1061, in temporaryDirectory
      AttributeError: 'NoneType' object has no attribute 'temp_dir

    or::

      Traceback (innermost last):
        ...
        Module ZODB.blob, line 495, in temp_dir
      TypeError: Blobs are not supported
  Problem
    You haven't configured a blob-storage for your extra database.
  Solution
    Please refer to David Glick's `comment in ticket #10130`__ for detailed
    information about the various ways to configure a blob-storage for
    additional mount-points.  The recommended way to accomplish this both
    for ZEO and non-ZEO setups is to use `collective.recipe.filestorage`__
    and adjust your buildout with the following::

      [buildout]
      ...
      parts =
          ...
          filestorage
          instance

      [filestorage]
      recipe = collective.recipe.filestorage
      blob-storage = var/blobstorage-%(fs_part_name)s
      parts =
          foo

    Please note that for the "parts" setting in the "buildout" section it is
    important to list "filestorage" before any parts installing Zope or ZEO.
    The "parts" setting in the "filestorage" section, however, represents
    a list of filestorage sub-parts to be generated, one per line.  Further
    details can be found in the `documentation of the recipe`__.

  .. __: http://dev.plone.org/plone/ticket/10130#comment:5
  .. __: http://pypi.python.org/pypi/collective.recipe.filestorage
  .. __: http://pypi.python.org/pypi/collective.recipe.filestorage


FAQ
===

Is it possible to use "plone.app.blob" in installations not based on `zc.buildout`_?

  Yes, but that would require some additional steps, since it depends on ZODB
  3.8, but Plone currently ships with Zope 2.10, which still comes with
  ZODB 3.7.  So, to make things work you could either install the `required
  versions`__ of all additionally needed packages into your ``lib/python/``
  directory or use the respective eggs and make sure they get preferred over
  their older versions on ``import``, for example by setting up
  ``PYTHONPATH``.

  .. __: http://dev.plone.org/plone/browser/plone.app.blob/trunk/setup.py#L35

  Alternatively it should also be possible to install the package using
  `easy_install`_, which would automatically install its dependencies
  including ZODB 3.8, too.  Again you would need to set up your ``PYTHONPATH``
  to make sure the desired versions are used.  However, installing the package
  like this is likely to have side effects on other Zope/Plone instances on
  your system, so you probably want to use `virtualenv`_ here at least.

  .. _`easy_install`: http://peak.telecommunity.com/DevCenter/EasyInstall
  .. _`virtualenv`: http://pypi.python.org/pypi/virtualenv

  Overall, to get started without too much pain, a buildout-based
  installation is recommended |---| for example the `provided buildout`_.

Will this be available for Plone 2.5.x?

  Yes, support for the 2.5 series is planned and next on the agenda.

What about image support, i.e. a drop-in for ``ATImage`` content?

  While just replacing the primary field in ``ATImage``'s schemata should
  probably already work quite well, proper image support is planned for a
  later release.  "proper" here means using a sub-typing approach as
  `presented by Rocky Burt`__ in Naples, which will have several advantages
  including a cleaner and better structured code, but will also take a little
  longer to implement.

  .. __: http://www.serverzen.com/training/subtyping-unleashed

Strange messages like ``Exception exceptions.OSError: (2, 'No such file or
directory', '.../tmpZvxjZB') in <bound method _TemporaryFileWrapper.__del__ of
<closed file '<fdopen>', mode 'w+b' at 0x7317650>> ignored`` get written to
the logs whenever a file is uploaded. Is that an error or something to worry
about?

  No, that's fine, it's just a small annoyance, that should be fixed
  eventually. In case you care, the problem is that the zope publisher creates
  a temporary file for each upload it receives.  Once the upload has finished
  that temporary file is passed to the blob machinery, which moves it into
  its blob storage.  However, at the end of the request the wrapper class for
  temporary files tries to remove the file as well, since well, it's supposed
  to be temporary.  At that time the file is already gone though, and the
  above warning is issued.

I have a ZEO setup with the server and clients running on separate machines.
Why do I get blobs stored in my ZEO clients' blobstorage directories and not
only on the server?

  ZEO clients cache blobs the first time they are fetched. Unfortunately the
  cache is not cleaned automatically when the instances are stopped and will
  keep growing. In addition, if you manually delete the files without
  restarting, the ZEO client will still expect to find them.  ZODB 3.9, which
  is used by Plone 4, introduces a cache size control that alleviates the
  problem.  Plone 3.x and earlier can only be used with ZODB 3.8.x, though.
  However, Sasha Vincic has written a `workaround for Plone 2.5.x`__ that
  invalidates the existing reference causing the blob data to be fetched
  again from the ZEO server should it be missing.  The patch has been merged_
  and is available from version 1.0b11.

  .. __: http://dev.plone.org/plone/changeset/32170
  .. _`merged`: http://dev.plone.org/plone/changeset/33100

.. TODO: answer the following...
.. <jonstahl> Given the overall clutter and confusion in the
..   broader file system storage product space, it might be helpful to expand
..   the Overview paragraph a bit. The things I'm wondering are: how does
..   Blob differ from FSS? Is it different from other blob implementations?
..   Are there things naive people might expect of plone.app.blob that it
..   *doesn't* do? (e.g. massive increase the speed of serving large files.
..   This doesn't really fully replace tramline, right?
.. <jonstahl> A bit of information on how you can use
..   plone.app.blog in your custom content types might helpful too.


Feedback
========

Any kind of feedback like bug reports, suggestions, feature requests and most
preferably success stories is most welcome and much appreciated. Especially,
it would be interesting to hear about success or problems with migration of
existing content and installations on platforms other than OSX.

So please feel free to file tickets in the `issue tracker`_, contact me on
`#plone`_, `#plone-framework`_, the `plone developer mailing list`_ or
directly via `email`_.

  .. _`issue tracker`: http://plone.org/products/plone.app.blob/issues
  .. _`#plone`: irc://irc.eu.freenode.net/plone
  .. _`#plone-framework`: irc://irc.eu.freenode.net/plone-framework
  .. _`plone developer mailing list`: mailto:plone-developers@lists.sourceforge.net
  .. _`email`: mailto:az_at_zitc_dot_de

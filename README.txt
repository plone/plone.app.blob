ZODB 3.8 blob support for Plone
===============================

Overview
--------

This package aims to be an add-on for Plone 3.x to integrate ZODB 3.8's blob
support, which means that large binary data can be managed by the ZODB, but
separately from your usual ``FileStorage`` database, i.e. ``Data.fs``.  This
has several advantages, most importantly a much smaller ``Data.fs`` and better
performance both cpu- as well as memory-wise.


Status
------

At the moment the integration is in a working state, but needs more testing in
real projects. The provided blob-based content type should be more or less
safely usable as a drop-in replacement for ``ATFile``.  As such it has been
successfully tested against all ``CMFPlone`` and ``ATContentTypes`` tests.
Instructions for replicating the necessary test setup and running these tests
youself can be found at http://dev.plone.org/plone/changeset/18321.

In addition, up-to-date information about the integration and the current
status can be found in the corresponding enhancement ticket at
http://dev.plone.org/plone/ticket/6805.


Installation
------------

The easiest way to get ZODB blob support in Plone 3 is to use this package
with installations based on `zc.buildout`_.  To get started you will simply
need to add the package to your "eggs" and "zcml" sections, run buildout,
restart your Plone instance and install the "plone.app.blob" package using
the quick-installer or via the "Add-on Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

A sample buildout configuration file, i.e. ``buildout.cfg``, could look like
this::

  [buildout]
  parts = plone zope2 instance
  find-links =
      http://dist.plone.org
      http://effbot.org/downloads
      http://download.zope.org/ppix/ 
      http://download.zope.org/distribution/
  eggs = elementtree

  [plone]
  recipe = plone.recipe.plone

  [zope2]
  recipe = plone.recipe.zope2install
  url = ${plone:zope2-url}

  [instance]
  recipe = plone.recipe.zope2instance
  zope2-location = ${zope2:location}
  blob-storage = var/blobstorage
  user = admin:admin
  products = ${plone:products}
  eggs =
      ${buildout:eggs}
      ${plone:eggs}
      plone.app.blob
  zcml = plone.app.blob

You can also use this ``buildout.cfg`` to create a fresh Plone installation by
storing it -- preferably in an empty directory, downloading `bootstrap.py
<http://svn.zope.org/*checkout*/zc.buildout/trunk/bootstrap/bootstrap.py>`_
into the same directory and issueing the following commands::

  $ python bootstrap.py
  $ ./bin/buildout
  $ ./bin/instance fg

After that you would as usual create a "Plone Site" via the `ZMI`_ and either
select the "plone.app.blob" extension profile at creation time or again
install the "plone.app.blob" package using one of the above mentioned methods.

  .. _`ZMI`: http://localhost:8080/manage

For your convenience a working buildout configuration, including
``bootstrap.py`` and ``buildout.cfg``, is provided as a subversion checkout at
`http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0`__.

  .. __: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0

More detailed instructions on how to use buildout can be found in the
`accompanying README.txt`__ as well as in the excellent `buildout tutorial`_
on `plone.org`_.

  .. __: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0/README.txt
  .. _`buildout tutorial`: http://plone.org/documentation/tutorial/buildout
  .. _`plone.org`: http://plone.org/


Migrating existing content
--------------------------

In-place content migration is provided for existing ``ATFile`` content. The
`Products.contentmigration`_ package is required for this to work. To install
this package you will again need to add its name to the "eggs" and "zcml"
section of your ``buildout.cfg`` -- please see the already mentioned `sample
buildout.cfg`_ for details.

  .. _`Products.contentmigration`: http://pypi.python.org/pypi/Products.contentmigration/
  .. _`sample buildout.cfg`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/plone-3.0/buildout.cfg

In order to then migrate your existing file content to blobs you can use the
migration interface provided at http://localhost:8080/plone/@@blob-migration,
where "plone" should be replaced with the id of your "Plone Site" object.  The
page will show you the number of available `ATFile` instances and lets you
convert them to the provided blob content type by clicking a button.


Troubleshooting
---------------

The following are some known issues, that will hopefully go away soon enough.
In the meantime here are the recommended workarounds:

"Invalid plugin id" Exception
  Symptom
    When trying to create a "Plone Site" you're getting an error like::

      Error Type: KeyError
      Error Value: 'Invalid plugin id: credentials_basic_auth'
  Problem
    Your version of ``Products.PluggableAuthService`` is too old -- you need
    1.5.2 or newer (please see http://www.zope.org/Collectors/PAS/59 for more
    information about this).
  Solution
    Please use the `provided buildout`_, add the `1.5 branch`_ as a develop
    egg to your buildout or wait a couple of days until Plone 3.0.4 has been
    released, which should also fix the problem.

  .. _`provided buildout`: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0
  .. _`1.5 branch`: http://svn.zope.org/Products.PluggableAuthService/branches/1.5/

Getting distribution for 'archetypes.schemaextender>1.0a1'
  Symptom
    When running buildout you're getting an error like::

      While:
        Installing instance.
        Getting distribution for 'archetypes.schemaextender>1.0a1'.
      Error: Couldn't find a distribution for 'archetypes.schemaextender>1.0a1'.
  Problem
    "plone.app.blob" requires some recent changes in
    "archetypes.schemaextender", which haven't been properly released yet.
  Solution
    Please use the `provided buildout`_, add ``archetypes.schemaextender``'s
    `trunk`_ as a development egg to your buildout or wait for the next
    release, very likely to be 1.0b1.

    .. _`trunk`: http://svn.plone.org/svn/archetypes/archetypes.schemaextender/trunk/

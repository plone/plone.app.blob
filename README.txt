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
storing it — preferably in an empty directory, downloading `bootstrap.py
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
section of your ``buildout.cfg`` — please see the already mentioned `sample
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


Getting distribution for 'Products.PluggableAuthService>=1.5.2'
  Symptom
    When running buildout you're getting an error like::
  
      Getting distribution for 'Products.PluggableAuthService>=1.5.2'.
      error: /var/folders/b0/b0C9MkEYEUyR1+20GCJohk+++TI/-Tmp-/easy_install-0ncZ-t/Products.PluggableAuthService-1.5.2/Products/PluggableAuthService/version.txt: No such file or directory
      An error occured when trying to install Products.PluggableAuthService 1.5.2.Look above this message for any errors thatwere output by easy_install.
  Problem
    The `tarball`_ for version 1.5.2 of `Products.PluggableAuthService`_ is
    currently `missing some files`_ and therefore cannot be used.
  Solution
    Please use the `provided buildout`_, add the `1.5 branch`_ as a develop
    egg to your buildout or wait until a complete tarball has been uploaded.

  .. _`tarball`: http://pypi.python.org/packages/source/P/Products.PluggableAuthService/Products.PluggableAuthService-1.5.2.tar.gz#md5=e51a3ea2dc9fdd3ca612d48a6b2aa9bf
  .. _`Products.PluggableAuthService`: http://cheeseshop.python.org/pypi/Products.PluggableAuthService/
  .. _`missing some files`: https://bugs.launchpad.net/zope-pas/+bug/161287/comments/6
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

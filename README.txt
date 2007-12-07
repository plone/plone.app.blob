ZODB 3.8 blob support for Plone
===============================

Overview
--------

This package aims to be an add-on for Plone 3.x integrating ZODB 3.8's blob
support, which allows large binary data to be managed by the ZODB, but
separately from your usual ``FileStorage`` database, i.e. ``Data.fs``.  This
has several advantages, most importantly a much smaller ``Data.fs`` and better
performance both cpu- as well as memory-wise.


Status
------

At the moment the integration is in a working state, but needs more field
testing.  The provided blob-based content type should be more or less safely
usable as a drop-in replacement for ``ATFile``. As such it has been
successfully tested against all ``CMFPlone`` and ``ATContentTypes`` tests.
Instructions for replicating the necessary test setup and running these tests
yourself can be found at http://dev.plone.org/plone/changeset/18321.

More detailed an up-to-date information about the integration and the current
status can be found in the corresponding `plone enhancement ticket`_.

  .. _`plone enhancement ticket`: http://dev.plone.org/plone/ticket/6805
  .. |--| unicode:: U+2013   .. en dash
  .. |---| unicode:: U+2014  .. em dash


Requirements
------------

Plone 3.0 or newer.  The package has been developed and testet on Plone 3.0.3,
but should also work with earlier versions of the 3.0 series.  However, as
those are only bug-fix releases it might be a good idea to upgrade anyway.


Installation
------------

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
  parts = plone zope2 instance
  find-links =
      http://dist.plone.org
      http://download.zope.org/ppix/ 
      http://download.zope.org/distribution/
      http://effbot.org/downloads
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

For your convenience a working buildout configuration, including
``bootstrap.py`` and ``buildout.cfg``, is provided as a subversion checkout at
`http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0`__.

  .. __: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0

More detailed instructions on how to set things up (including a working zeo
configuration) as well as some background information on blobs |---| or in
other words the story of an "early adopter" |---| can be found in `Ken
Manheimer's wiki`__.  This is a highly useful resource and recommended read
for people trying to give blobs a spin.

  .. __: http://myriadicity.net/Sundry/PloneBlobs

In addition, more information on how to use buildout is available in the
`accompanying README.txt`__ as well as in `Martin's`_ excellent `buildout
tutorial`_ on `plone.org`_.

  .. __: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0/README.txt
  .. _`Martin's`: http://martinaspeli.net/
  .. _`buildout tutorial`: http://plone.org/documentation/tutorial/buildout
  .. _`plone.org`: http://plone.org/


Migrating existing content
--------------------------

In-place content migration is provided for existing ``ATFile`` content. The
`Products.contentmigration`_ package is required for this to work. To install
this package you will again need to add its name to the "eggs" and "zcml"
section of your ``buildout.cfg``, so that it reads like::

  [instance]
  ...
  eggs =
      ${buildout:eggs}
      ${plone:eggs}
      plone.app.blob
      Products.contentmigration
  zcml =
      plone.app.blob
      Products.contentmigration

You can also refer to the above mentioned `sample buildout.cfg`_ for details.

  .. _`Products.contentmigration`: http://pypi.python.org/pypi/Products.contentmigration/
  .. _`sample buildout.cfg`: http://dev.plone.org/plone/browser/plone.app.blob/buildouts/plone-3.0/buildout.cfg

In order to then migrate your existing file content to blobs you can use the
migration interface provided at http://localhost:8080/plone/@@blob-migration,
where "plone" should be replaced with the id of your "Plone Site" object.  The
page will show you the number of available ``ATFile`` instances and lets you
convert them to the provided blob content type by clicking a button.


Troubleshooting
---------------

The following are some known issues, that will hopefully be resolved soon
enough.  In the meantime here are the recommended workarounds:

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
    Please use the `provided buildout`_, add the `1.5 branch`_ as a
    `development egg`_ to your buildout or wait a couple of days until Plone
    3.0.4 has been released, which should also fix the problem.

  .. _`provided buildout`: http://svn.plone.org/svn/plone/plone.app.blob/buildouts/plone-3.0
  .. _`1.5 branch`: http://svn.zope.org/Products.PluggableAuthService/branches/1.5/
  .. _`development egg`: http://plone.org/documentation/tutorial/buildout/understanding-buildout.cfg


**Getting distribution for 'archetypes.schemaextender>1.0a1'**

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
    `trunk`_ as a `development egg`_ to your buildout or wait for the next
    release, very likely to be 1.0b1.

  .. _`trunk`: http://svn.plone.org/svn/archetypes/archetypes.schemaextender/trunk/


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


FAQ
---

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

  __: http://www.serverzen.com/training/subtyping-unleashed



Feedback
--------

Any kind of feedback like bug reports, suggestions, feature requests and most
preferably success stories is most welcome and much appreciated. Especially,
it would be interesting to hear about success or problems with migration of
existing content and installations on platforms other than OSX.

So please feel free to post comments to the above mentioned `plone enhancement
ticket`_, file tickets in the `plone issue tracker`_ (assigning them to me ;))
or contact me on `#plone`_, through the `plone developer mailing list`_ or
directly via `email`_.

  .. _`plone issue tracker`: http://dev.plone.org/plone/
  .. _`#plone`: irc://irc.eu.freenode.net/plone
  .. _`plone developer mailing list`: mailto:plone-developers@lists.sourceforge.net
  .. _`email`: mailto:az_at_zitc_dot_de

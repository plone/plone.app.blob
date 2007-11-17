from setuptools import setup, find_packages

version = '0.1'

setup(name='plone.app.blob',
      version=version,
      description="ZODB 3.8 Blob support for Plone 3.x",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zodb blob support plone',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/plone/plone.app.blob',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone.app'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'ZODB3 >=3.8.0b2,<3.8.999',
          'zope.interface >=3.3,<3.3.999',
          'zope.testing >=3.0,<3.3.999',
          'ZConfig >=2.4a2,<2.4.999',
          'zdaemon >=1.4a2,<1.4.999',
          'zope.proxy >=3.4,<3.4.999',
          'zodbcode >=3.4,<3.4.999',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

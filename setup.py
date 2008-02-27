from setuptools import setup, find_packages

version = '1.0b1'
readme = open("README.txt").read()

setup(name = 'plone.app.blob',
      version = version,
      description = 'ZODB 3.8 blob support for Plone 3.x',
      long_description = readme[readme.find('Overview'):],
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      keywords = 'zodb blob support plone integration',
      author = 'Andreas Zeidler - Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://dev.plone.org/plone/ticket/6805',
      download_url = 'http://cheeseshop.python.org/pypi/plone.app.blob/',
      license = 'GPL',
      packages = find_packages(),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires=[
          'setuptools',
          'ZODB3 >=3.8.0b2,<3.8.999',
          'zope.interface >=3.3,<3.3.999',
          'zope.testing >=3.0,<3.3.999',
          'ZConfig >=2.4a2,<2.4.999',
          'zdaemon >=1.4a2,<1.4.999',
          'zope.proxy >=3.4,<3.4.999',
          'zodbcode >=3.4,<3.4.999',
          'archetypes.schemaextender >=1.0b1',
      ],
)


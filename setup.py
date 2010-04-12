from setuptools import setup, find_packages
from os.path import join

name = 'plone.app.blob'
path = ['src'] + name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()
readme = open('README.txt').read()
history = open(join('docs', 'HISTORY.txt')).read()
tests_require = ['collective.monkeypatcher']

setup(name = name,
      version = version,
      description = 'ZODB 3.8 blob support for Plone 3.x',
      long_description = readme[readme.find('\n\n'):] + '\n' + history,
      keywords = 'zodb blob support plone integration',
      author = 'Andreas Zeidler - Plone Foundation',
      author_email = 'plone-developers@lists.sourceforge.net',
      url = 'http://plone.org/products/plone.app.blob',
      download_url = 'http://pypi.python.org/pypi/plone.app.blob/',
      license = 'GPL',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['plone', 'plone.app'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      install_requires=[
        'setuptools',
        'ZODB3 >=3.8.1',
        'zope.proxy >=3.4',
        'archetypes.schemaextender >=1.6',
        'plone.app.imaging >1.0b9',
        'plone.scale',
      ],
      tests_require = tests_require,
      extras_require = {'test': tests_require},
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
      entry_points = '''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
)

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.5.3'

long_description = (
    read('README.txt')
    + '\n' +
    read('src', 'plone', 'app', 'blob', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n'
    )

tests_require = [
    'collective.monkeypatcher',
    'Products.contentmigration',
    'plone.app.imaging [test]']

setup(name='plone.app.blob',
      version=version,
      description='ZODB blob support for Plone',
      #long_description=readme[readme.find('\n\n'):] + '\n' + history,
      long_description=long_description,
      keywords='zodb blob support plone integration',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://plone.org/products/plone.app.blob',
      download_url='http://pypi.python.org/pypi/plone.app.blob/',
      license='GPL version 2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['plone', 'plone.app'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      install_requires=[
        'setuptools',
        'ZODB3 >=3.8.1',
        'zope.proxy >=3.4',
        'archetypes.schemaextender >=1.6',
        'plone.app.imaging >1.0b9',
        'plone.scale',
      ],
      tests_require=tests_require,
      extras_require={'test': tests_require},
      classifiers=[
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
      ],
      entry_points='''
        [z3c.autoinclude.plugin]
        target = plone
      ''',
)

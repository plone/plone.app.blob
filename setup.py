# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.7.5'

long_description = (
    read('README.rst')
    + '\n' +
    read('src', 'plone', 'app', 'blob', 'README.txt')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
)

tests_require = [
    'Products.contentmigration',
    'collective.monkeypatcher',
    'plone.app.imaging',
    'plone.app.testing',
]

setup(
    name='plone.app.blob',
    version=version,
    description='ZODB blob support for Plone',
    long_description=long_description,
    keywords='zodb blob support plone integration',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='http://plone.org/products/plone.app.blob',
    download_url='https://pypi.python.org/pypi/plone.app.blob/',
    license='GPL version 2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.app'],
    include_package_data=True,
    platforms='Any',
    zip_safe=False,
    install_requires=[
        'Products.MimetypesRegistry',
        'ZODB3 >=3.8.1',
        'archetypes.schemaextender >=1.6',
        'plone.app.imaging >1.0b9',
        'plone.scale',
        'setuptools',
        'six',
        'zope.proxy >=3.4',
    ],
    tests_require=tests_require,
    extras_require={'test': tests_require},
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Web Environment',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
    ],
    entry_points='''
        [z3c.autoinclude.plugin]
        target = plone
    ''',
)

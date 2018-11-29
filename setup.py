#!/usr/bin/env python

from setuptools import setup, find_packages

from usp.__about__ import __version__


def __readme():
    with open('README.rst', mode='r', encoding='utf-8') as f:
        return f.read()


tests_require = [

    # Mock HTTP server
    'httpretty==0.9.6',

    # Running tests
    'pytest==4.0.1',

]

setup(
    name='ultimate_sitemap_parser',
    version=__version__,
    description='Ultimate Sitemap Parser',
    long_description=__readme(),
    author='Linas Valiukas, Hal Roberts, Media Cloud project',
    author_email='linas@media.mit.edu, hroberts@cyber.law.harvard.edu',
    url='https://github.com/berkmancenter/mediacloud-ultimate_sitemap_parser',
    keywords="sitemap sitemap-xml parser",
    packages=find_packages(exclude=['tests']),
    zip_safe=True,
    install_requires=[

        # No dunder methods
        'attrs==18.2.0',

        # Parsing arbitrary dates (sitemap date format is standardized but some implementations take liberties)
        'python-dateutil==2.7.5',

        # Making HTTP requests
        'requests==2.20.1',
        'idna==2.7',

    ],
    setup_requires=[

        # Running tests as part of setup.py
        'pytest-runner==4.2',

    ],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Text Processing :: Indexing',
        'Topic :: Text Processing :: Markup :: XML',
    ]
)

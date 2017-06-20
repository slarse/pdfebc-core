# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

test_requirements = ['pytest>=3.1.1', 'pytest-cov>=2.5.1']
required = ['appdirs>=1.4.3']

setup(
    name='pdfebc-core',
    version='0.2.0',
    description=('Core functions of the pdfebc tools. The pdfebc tools is (going to be) a .'
                 'set of tools for compressing PDF files to e-reader friendly sizes.'),
    long_description=readme,
    author='Simon Larsén',
    author_email='slarse@kth.se',
    url='https://github.com/slarse/pdfebc-core',
    download_url='https://github.com/slarse/pdfebc-core/archive/v0.2.0.tar.gz',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    tests_require=test_requirements,
    install_requires=required
)

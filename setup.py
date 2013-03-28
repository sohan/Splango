#!/usr/bin/env python
from setuptools import setup, find_packages

# from debug-toolbar!

setup(
    name='Splango',
    version='0.1',
    description='Split (A/B) testing library for Django',
    author='Shimon Rura',
    author_email='shimon@rura.org',
    url='http://github.com/shimon/Splango',
    packages=find_packages(exclude=('tests', 'example')),
    package_data={'splango': ['templates/*.html', 'templates/*/*.html']},
    tests_require=[
        'django>=1.3,<1.5',
    ],
    test_suite='runtests.runtests',
)

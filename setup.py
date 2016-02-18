#!/usr/bin/env python

from beanstalk import __version__
from setuptools import find_packages, setup

setup(
    name='beanstalk-py',
    version=__version__,

    author='silence-money',
    author_email='ifidot@gmail.com',
    description='',
    long_description=''' ''',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/silent-money/beanstalk-py',
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'PyYAML',
    ]
)

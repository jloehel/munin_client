#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function

from setuptools import setup


def requires(filename):
    """Returns a list of all pip requirements

    :param filename: the Pip requirement file (usually 'requirements.txt')
    :return: list of modules
    :rtype: list
    """
    modules = []
    with open(filename, 'r') as pipreq:
        for line in pipreq:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            modules.append(line)
    return modules


setup(
    name="munin_client",
    version="1.0.0",
    license="MIT",
    author="Jürgen Löhel",
    author_email="jloehel@suse.com",
    url='https://github.com/jloehel/munin_client',
    description="A simple python munin client.",
    keywords=["munin", "monitoring", "client", "simple"],
    packages=["munin_client"],
    package_dir={'munin_client': ''},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires('requirements.txt'),
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'pytest-catchlog', "pytest-flask"],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        ]
)

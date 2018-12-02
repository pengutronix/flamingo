#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import flamingo

setup(
    include_package_data=True,
    name='flamingo',
    version=flamingo.VERSION_STRING,
    author='Florian Scherf',
    url='https://github.com/pengutronix/flamingo',
    author_email='python@pengutronix.de',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=[
        'jinja2',
        'docutils',
        'aiohttp-json-rpc',
        'aionotify',
        'coloredlogs',
    ],
    scripts=[
        'bin/flamingo-build',
        'bin/flamingo-server',
        'bin/flamingo-shell',
    ],
)

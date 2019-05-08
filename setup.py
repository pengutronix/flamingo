#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import flamingo

EXTRAS_REQUIRE = {
    'live-server': [
        'aiohttp-json-rpc==0.12',
        'aionotify==0.2.0',
    ],
    'chardet': [
        'chardet',
    ],
    'pygments': [
        'pygments',
    ],
    'feeds': [
        'feedgen==0.7.0',
    ],
    'coloredlogs': [
        'coloredlogs',
    ],
    'ipython': [
        'ipython',
    ]
}

EXTRAS_REQUIRE['full'] = sum([v for k, v in EXTRAS_REQUIRE.items()], [])

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
        'pyyaml',
        'beautifulsoup4',
    ],
    scripts=[
        'bin/flamingo',
        'bin/_flamingo-init',
        'bin/_flamingo-build',
        'bin/_flamingo-server',
        'bin/_flamingo-shell',
    ],
    entry_points={
        'pytest11': [
            'flamingo = flamingo.pytest',
        ],
    },
    extras_require=EXTRAS_REQUIRE,
)

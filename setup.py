#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

import flamingo

INSTALL_REQUIRES = [
    'jinja2>=3.0.0',
    'docutils',
    'pyyaml',
    'beautifulsoup4',
    'rlpython',
]

EXTRAS_REQUIRE = {
    'live-server': [
        'aiohttp>=3,<4',
        'pygments',
    ],
    'chardet': [
        'chardet',
    ],
    'pygments': [
        'pygments',
    ],
    'markdown': [
        'markdown',
    ],
    'feeds': [
        'feedgen==0.7.0',
    ],
    'thumbnails': [
        'pillow',
    ],
    'photoswipe': [
        'pillow',
    ],
    'coloredlogs': [
        'coloredlogs',
    ],
    'sphinx-themes': [
        'sphinx>=4.5.0',
        'sphinx_rtd_theme>=1.0.0',
    ],
}

EXTRAS_REQUIRE['full'] = sum([v for k, v in EXTRAS_REQUIRE.items()], [])

if 'FLAMINGO_TEST' in os.environ:
    INSTALL_REQUIRES = INSTALL_REQUIRES + EXTRAS_REQUIRE['full']

setup(
    include_package_data=True,
    name='flamingo',
    version=flamingo.VERSION_STRING,
    author='Florian Scherf',
    url='https://github.com/pengutronix/flamingo',
    author_email='python@pengutronix.de',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    scripts=[
        'bin/flamingo',
        'bin/_flamingo-args',
        'bin/_flamingo-init',
        'bin/_flamingo-build',
        'bin/_flamingo-shell',
        'bin/_flamingo-server',
    ],
    entry_points={
        'pytest11': [
            'flamingo = flamingo.pytest',
        ],
    },
)

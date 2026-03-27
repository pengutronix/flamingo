#!/usr/bin/env python3

import os
import runpy
import sys

from flamingo.core.utils.cli import error, get_raw_parser


def main():
    if not sys.version_info >= (3, 11, 0):
        exit(error("flamingo needs at least python3.11 to run properly"))

    PREFIX = "_flamingo-"
    PATH = os.path.dirname(__file__)

    scripts = {i[len(PREFIX) :]: os.path.join(PATH, i) for i in os.listdir(PATH) if i.startswith(PREFIX)}

    parser = get_raw_parser(prog="flamingo")
    parser.add_argument("command", choices=list(scripts.keys()))
    args = parser.parse_args(sys.argv[1:2])

    sys.argv = [sys.argv[0]] + sys.argv[2:]

    runpy.run_path(scripts[args.command])


if __name__ == "__main__":
    main()

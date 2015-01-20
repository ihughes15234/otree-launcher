#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

"""Command line interface

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys
import shutil
import argparse

from . import cons, core, gui


# =============================================================================
# CONSTANTS
# =============================================================================

logger = cons.logger


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_parser():
    """Create a parser for install from command line

    """

    def dirpath(value):
        value = os.path.abspath(value)
        if os.path.isdir(value):
            msg = "'{}' directory already exists".format(value)
            raise argparse.ArgumentTypeError(msg)
        os.makedirs(value)
        return value

    parser = argparse.ArgumentParser(
        prog=cons.PRJ, version=cons.STR_VERSION, description=cons.DOC
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--gui", dest="gui", action="store_true",
        help="execute the the visual enviroment of the installer"
    )
    group.add_argument(
        "-w", "--wrkpath", dest="wrkpath", type=dirpath,
        metavar="WORK_PATH", help="The directory must not exists "
    )
    return parser


def run():
    """Execute the command line installer

    """
    parser = get_parser()
    args = parser.parse_args()
    if args.gui:
        gui.run()
    else:
        core.full_install_and_run(args.wrkpath)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

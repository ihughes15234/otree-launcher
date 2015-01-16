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
import atexit
import time

from . import cons, core


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
        force = "-f" in sys.argv or "--force" in sys.argv
        if force and os.path.isdir(value):
            shutil.rmtree(value)
        elif os.path.isdir(value):
            msg = "'{}' directory already exists".format(value)
            raise argparse.ArgumentTypeError(msg)
        os.makedirs(value)
        return value

    parser = argparse.ArgumentParser(
        prog=cons.PRJ, version=cons.STR_VERSION, description=cons.DOC
    )
    parser.add_argument(
        "-f", "--force", dest="force", action="store_true",
        help="If the destination directory already exist remove it first."
    )
    parser.add_argument(
        dest="wrkpath", type=dirpath, metavar="WORK_PATH",
        help="Local path to clone oTree. "
    )
    return parser


def run():
    """Execute the command line installer

    """

    # retrieve parser
    parser = get_parser()
    args = parser.parse_args()

    # start install
    wrkpath = args.wrkpath
    logger.info("Downloading oTree on '{}'".format(wrkpath))
    core.download(wrkpath)

    logger.info("Initiating oTree installer on '{}'".format(wrkpath))
    core.install(wrkpath)

    # run
    proc = core.execute(wrkpath)

    logger.info("Lunching webbrowser...")
    time.sleep(cons.OTREE_SPAN_SLEEP)
    core.open_webbrowser()

    # clean
    def clean(proc):
        if proc.returncode is None:
            proc.kill()

        runner_path = os.path.join(wrkpath, cons.OTREE_DIR, cons.RUNNER)
        msg = "If you want to run again execute {}".format(runner_path)
        msglen = len(msg)

        logger.info("=" * msglen)
        logger.info(msg)
        logger.info("=" * msglen)

    atexit.register(clean, proc)

    proc.wait()

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOCS
# =============================================================================

"""Installer for oTree (http://otree.org/)

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys
import subprocess
import shlex
import logging
import argparse

import sh


# =============================================================================
# CONSTANTS
# =============================================================================

PRJ = "install"

DOC = __doc__

# : The project version as tuple of strings
VERSION = ("0", "1")

# : The project version as string
STR_VERSION = ".".join(VERSION)
__version__ = STR_VERSION

OTREE_REPO = "git@github.com:oTree-org/oTree.git"

IS_WINDOWS = sys.platform.startswith("win")

SYSTEM_DEPENDENCIES_ERRORS = []


# =============================================================================
# LOGGER
# =============================================================================

def _get_logger():
    logger = logging.getLogger(PRJ)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s|%(asctime)s] %(name)s > %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = _get_logger()


# =============================================================================
# SYSTEM DEPENDENCIES CHECK
# =============================================================================

try:
    sh.git(help=True)
except sh.CommandNotFound as err:
    SYSTEM_DEPENDENCIES_ERRORS.append(
        "git not found. For instll see: http://git-scm.com/"
    )

if SYSTEM_DEPENDENCIES_ERRORS:
    errors = "\n\t".join(SYSTEM_DEPENDENCIES_ERRORS)
    msg = "System Error found:\n\t{}".format(errors)
    logger.error(msg)
    sys.exit(1)


# =============================================================================
# FUNCTIONS
# =============================================================================

def get_parser():

    def dirpath(value):
        value = os.path.abspath(value)
        if os.path.isdir(value):
            msg = "'{}' directory already exists".format(value)
            raise argparse.ArgumentTypeError(msg)
        os.makedirs(value)
        return value

    parser = argparse.ArgumentParser(
        prog=PRJ, version=STR_VERSION, description=DOC
    )
    parser.add_argument(
        dest="wrkpath", type=dirpath, metavar="WORK_PATH",
        help=(
            "Local path to clone oTree. "
            "The destination directory must not already exist."
        )
    )
    return parser


def git_clone_otree_project(path):
    pass







# =============================================================================
# FUNCTIONS
# =============================================================================


def main():
    parser = get_parser()
    args = parser.parse_args()

    # main loop
    logger.info("Initiating installer on '{}'".format(args.wrkpath))
    #~ logger.info("




# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()

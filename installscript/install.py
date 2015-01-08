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
import shutil
import logging
import argparse
import contextlib

import sh

import virtualenv


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

OTREE_DIR = "oTree"

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
        "'git' command not found. For install see: http://git-scm.com/"
    )


# =============================================================================
# HELPER FUNCTIONS AND CONTEXT
# =============================================================================

@contextlib.contextmanager
def cd(path):
    original = os.getcwdu()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original)


def get_parser():

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
        prog=PRJ, version=STR_VERSION, description=DOC
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


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def validate_system_dependencies():
    if SYSTEM_DEPENDENCIES_ERRORS:
        errors = "\n\t".join(SYSTEM_DEPENDENCIES_ERRORS)
        msg = "System Error found:\n\t{}".format(errors)
        raise SystemError(msg)


def git_clone_otree_project(path, out=None, verbose=True):
    clonepath = os.path.join(path, OTREE_DIR)
    sh.git.clone(OTREE_REPO, clonepath, _out=out, _err=out, verbose=verbose)










# =============================================================================
# FUNCTIONS
# =============================================================================


def main():
    # check system
    try:
        validate_system_dependencies()
    except SystemError as err:
        logger.error(err.message)
        sys.exit(1)

    # retrieve parser
    parser = get_parser()
    args = parser.parse_args()

    # start install
    wrkpath = args.wrkpath
    logger.info("Initiating installer on '{}'".format(wrkpath))

    logger.info("Creating virtualenv...")
    virtualenv.create_environment(wrkpath)

    logger.info("Starting Git Clone...")
    git_clone_otree_project(wrkpath, logger.info)

    logger.info("Installing...")
    install_otree(wrkpath, logger.info)









# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()

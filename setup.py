#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


#==============================================================================
# DOCS
#==============================================================================

__doc__ = """This file is for package otree launcher"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys
import zipfile
import shutil
import logging
import datetime


# =============================================================================
# CONSTANTS
# =============================================================================

BUILD = datetime.datetime.now().isoformat()

PATH = os.path.abspath(os.path.dirname(__file__))

OTREE_PKG_PATH = os.path.join(PATH, "otree_launcher")

WORK_PATH = os.path.join(PATH, "_wrk")

DIST_PATH = os.path.join(PATH, "_dist")

MAIN_FILE_PATH = os.path.join(PATH, "run.py")

BUILD_DEPS_PATH = os.path.join(PATH, "build_deps")

PACKAGE_FNAME = "otree_deployer_VERSION_{}.zip".format(BUILD)

EXTENSIONS_TO_ZIP = (".py", ".csh", ".sh", ".bat", ".cfg", ".fish", ".exe")


# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.CRITICAL)


#==============================================================================
# FUNCTIONS
#==============================================================================

def create_dirs(*dirs_paths):
    for dpath in dirs_paths:
        if os.path.exists(dpath):
            logger.debug("Removing existing dir '{}' ".format(dpath))
            shutil.rmtree(dpath)
        logger.debug("Creating dir '{}' ".format(dpath))
        os.makedirs(dpath)


def list_zip_files(base_path, extensions):
    basename = os.path.basename(base_path)
    for dirpath, dirnames, filenames in os.walk(base_path):
        for fname in filenames:
            if os.path.splitext(fname)[-1] in extensions:
                fpath = os.path.join(dirpath, fname)
                aname = os.path.join(
                    basename, fpath.replace(base_path + os.path.sep, "", 1)
                )
                yield fpath, aname


def main():
    if "-v" in sys.argv or "--verbose" in sys.argv:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.info("Creating dir structures")
    create_dirs(WORK_PATH, DIST_PATH)

    zip_path = os.path.join(WORK_PATH, PACKAGE_FNAME)
    zip_dist_path = os.path.join(DIST_PATH, PACKAGE_FNAME)

    logger.info("Start compress...")
    with zipfile.ZipFile(zip_path, mode='w', allowZip64=True) as fp:

        for fpath, aname in list_zip_files(OTREE_PKG_PATH, EXTENSIONS_TO_ZIP):
            logger.debug("Adding '{}' -> '{}'".format(fpath, aname))
            fp.write(filename=fpath, arcname=aname)

        for fpath, aname in list_zip_files(BUILD_DEPS_PATH, EXTENSIONS_TO_ZIP):
            logger.debug("Adding '{}' -> '{}'".format(fpath, aname))
            fp.write(filename=fpath, arcname=os.path.basename(aname))

        logger.debug("Adding '{}' -> '{}'".format(MAIN_FILE_PATH, "run.py"))
        fp.write(filename=MAIN_FILE_PATH, arcname="run.py")

    logger.debug("Moving package to dist directory...")
    shutil.copyfile(zip_path, zip_dist_path)

    logger.info("Your launcher is here: '{}'".format(zip_dist_path))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()

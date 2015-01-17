#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


#==============================================================================
# DOCS
#==============================================================================

__doc__  = """This file is for package otree installer

"""

# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys
import zipfile
import shutil


# =============================================================================
# CONSTANTS
# =============================================================================

PATH = os.path.abspath(os.path.dirname(__file__))

OTREE_PKG_PATH = os.path.join(PATH, "otree_installer")

WORK_PATH = os.path.join(PATH, "_wrk")

DIST_PATH = os.path.join(PATH, "_dist")

MAIN_FILE_PATH = os.path.join(PATH, "install.py")

BUILD_DEPS_PATH = os.path.join(PATH, "build_deps")

PACKAGE_FNAME = "otree_ip.zip"

EXTENSIONS_TO_ZIP = (".py", ".csh", ".sh" ".bat", ".cfg", ".fish")


#==============================================================================
# FUNCTIONS
#==============================================================================

def create_dirs(*dirs_paths):
    for dpath in dirs_paths:
        if os.path.exists(dpath):
            shutil.rmtree(dpath)
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
    create_dirs(WORK_PATH, DIST_PATH)
    zip_path = os.path.join(WORK_PATH, PACKAGE_FNAME)
    with zipfile.ZipFile(zip_path, mode='w', allowZip64=True) as fp:
        for fpath, aname in list_zip_files(OTREE_PKG_PATH, EXTENSIONS_TO_ZIP):
            fp.write(filename=fpath, arcname=aname)
        fp.write(filename=MAIN_FILE_PATH, arcname="__main__.py")






# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()




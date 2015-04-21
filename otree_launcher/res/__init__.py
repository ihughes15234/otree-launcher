#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """oTree Launcher resources"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import sys


# =============================================================================
# CONSTANTS
# =============================================================================

IS_WINDOWS = sys.platform.startswith("win")

PATH = os.path.abspath(os.path.dirname(__file__))

if IS_WINDOWS:
    from ..libs import winext
    PATH = winext.shortpath(PATH)
else:
    PATH = PATH.decode("utf8")


# =============================================================================
# FUNCTIONS
# =============================================================================

def get(*parts):
    """Retrieve a full path to resourse or raises an IOError"""
    fpath = os.path.join(*parts)
    path = os.path.join(PATH, fpath)
    if os.path.exists(path):
        return path
    raise IOError("Resource '{}' not exists".format(fpath))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

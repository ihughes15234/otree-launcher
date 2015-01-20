#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Constants for all oTree installer

"""


# =============================================================================
# IMPORTS
# =============================================================================

import sys
import os
import logging


# =============================================================================
# PROJECT CONSTANTS
# =============================================================================

PRJ = "oTree-installer"

DOC = "Installer of oTree (http://otree.org)"

URL = "http://otree.org"

EMAIL = "chris@otree.org"

LICENSE = "License :: OSI Approved :: MIT License"

AUTHOR = "The oTree team"

SHORT_DESCRIPTION = DOC.splitlines()[0]

# : The project version as tuple of strings
VERSION = ("0", "2dev")

STR_VERSION = __version__ = ".".join(VERSION)

HOME_DIR = os.path.expanduser("~")

OTREE_CODE_URL = "https://github.com/oTree-org/oTree/archive/master.zip"

OTREE_CODE_FNAME = "otree_master.zip"

DOWNLOAD_OTREE_DIR = "oTree-master"

OTREE_DIR = "oTree"

REQUIREMENTS_FNAME = "requirements_base.txt"

OTREE_SPAN_SLEEP = 5

DEFAULT_OTREE_DEMO_URL = "http://localhost:8000/"


# =============================================================================
# PLATAFORM DEPENDENT CONSTANTS
# =============================================================================

IS_WINDOWS = sys.platform.startswith("win")

ENCODING = "UTF-8"

DULWICH_PKG = "dulwich-windows" if IS_WINDOWS else "dulwich"

INTERPRETER = "" if IS_WINDOWS else "bash"

END_CMD = " || goto :error \n" if IS_WINDOWS else ";\n"

SCRIPT_EXTENSION = "bat" if IS_WINDOWS else "sh"

SCRIPT_HEADER = [] if IS_WINDOWS else ["set -e;"]

SCRIPT_FOOTER = ["", ":error", "  exit /b %errorlevel%"] if IS_WINDOWS else []


# =============================================================================
# TEMPLATES FOS SCRIPTS
# =============================================================================

INSTALL_CMDS_TEMPLATE = """
python $VIRTUALENV_PATH $WRK_PATH
$ACTIVATE
pip install --upgrade -r $REQUIREMENTS_PATH
cd $OTREE_PATH
python $RUNSCRIPT resetdb --noinput
"""

RUNNER_SCRIPT_FNAME = "otree.{}".format(SCRIPT_EXTENSION)

RUNNER_CMDS_TEMPLATE = """
$ACTIVATE
cd $OTREE_PATH
python $RUNSCRIPT runserver
"""


# =============================================================================
# LOGGER
# =============================================================================

def logger():
    logger = logging.getLogger(PRJ)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '[%(levelname)s] %(name)s > %(message)s'
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

logger = logger()


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

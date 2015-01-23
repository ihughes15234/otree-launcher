#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# FUTURES
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOC
# =============================================================================

__doc__ = """Constants for all oTree launcher

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

PRJ = "oTree-launcher"

DOC = "Launcher of oTree (http://otree.org)"

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

APP_DATA = os.environ.get("APPDATA", HOME_DIR) if IS_WINDOWS else HOME_DIR

LAUNCHER_DIR = "otree-launcher" if IS_WINDOWS else ".otree-launcher"

LAUNCHER_DIR_PATH = os.path.join(HOME_DIR, ".otree-launcher")

DB_PATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.sqlite3")

ENCODING = "UTF-8"

INTERPRETER = "" if IS_WINDOWS else "bash"

VENV_SCRIPT_DIR = "Scripts" if IS_WINDOWS else "bin"

END_CMD = " || goto :error \n" if IS_WINDOWS else ";\n"

SCRIPT_EXTENSION = "bat" if IS_WINDOWS else "sh"

SCRIPT_HEADER = [] if IS_WINDOWS else ["set -e;"]

SCRIPT_FOOTER = ["", ":error", "  exit /b %errorlevel%"] if IS_WINDOWS else []


# =============================================================================
# TEMPLATES FOS SCRIPTS
# =============================================================================

INSTALL_CMDS_TEMPLATE = """
python "$VIRTUALENV_PATH" "$WRK_PATH"
$ACTIVATE
pip install --upgrade -r "$REQUIREMENTS_PATH"
cd "$OTREE_PATH"
python $RUNSCRIPT resetdb --noinput
"""

RUNNER_SCRIPT_FNAME = "otree_run.{}".format(SCRIPT_EXTENSION)

RUNNER_CMDS_TEMPLATE = """
$ACTIVATE
cd "$OTREE_PATH"
python "$RUNSCRIPT" runserver
"""


# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


# =============================================================================
# DIRECTORIES
# =============================================================================

if not os.path.isdir(LAUNCHER_DIR_PATH):
    os.makedirs(LAUNCHER_DIR_PATH)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

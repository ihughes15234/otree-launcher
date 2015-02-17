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
import datetime

from . import res

# =============================================================================
# PROJECT CONSTANTS
# =============================================================================

PRJ = "oTree Launcher"

DOC = "Launcher for oTree (http://otree.org)"

URL = "http://otree.org"

EMAIL = "chris@otree.org"

LICENSE = "License :: OSI Approved :: MIT License"

AUTHOR = "The oTree team"

SHORT_DESCRIPTION = DOC.splitlines()[0]

# : The project version as tuple of strings
VERSION = ("0", "3")

STR_VERSION = __version__ = ".".join(VERSION)

HOME_DIR = os.path.expanduser("~")

OTREE_REPO = "https://github.com/oTree-org/oTree.git"

REQUIREMENTS_FNAME = "requirements_base.txt"

OTREE_SPAN_SLEEP = 5

DEFAULT_OTREE_DEMO_URL = "http://localhost:8000/"

OTREE_SCRIPT_FNAME = "otree"

VENV_REQUIREMENTS_URL = (
    "https://raw.githubusercontent.com/oTree-org/oTree/master/"
    "requirements_base.txt"
)


# =============================================================================
# PLATAFORM DEPENDENT CONSTANTS
# =============================================================================

IS_WINDOWS = sys.platform.startswith("win")

LAUNCHER_DIR_PATH = os.path.join(
    os.environ.get("APPDATA", HOME_DIR) if IS_WINDOWS else HOME_DIR,
    "otree-launcher" if IS_WINDOWS else ".otree-launcher"
)

LAUNCHER_VENV_PATH = os.path.join(LAUNCHER_DIR_PATH, "venv")

LAUNCHER_TEMP_DIR_PATH = os.path.join(LAUNCHER_DIR_PATH, "temp")

LOG_FPATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.log")

DB_FPATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.db")

ENCODING = "UTF-8"

TERMINAL_CMD = (
    "start \"oTree Terminal\" /wait cmd /k" if IS_WINDOWS else
    "xterm -fa monaco -fs 10 -T \"oTree Terminal\" -e bash --init-file"
)

INTERPRETER = "" if IS_WINDOWS else "bash"

VENV_SCRIPT_DIR_PATH = os.path.join(LAUNCHER_VENV_PATH,
                                    "Scripts" if IS_WINDOWS else "bin")

ACTIVATE_PATH  = (
    os.path.join(VENV_SCRIPT_DIR_PATH, "activate.bat")
    if IS_WINDOWS else
    os.path.join(VENV_SCRIPT_DIR_PATH, "activate")
)


ACTIVATE_CMD = (
    "call \"{}\"".format(ACTIVATE_PATH)
    if IS_WINDOWS else
    "source \"{}\"".format(ACTIVATE_PATH)
)


DULWICH_CMD = "python \"{}\"".format(
    os.path.join(VENV_SCRIPT_DIR_PATH, "dulwich")
)

PIP_CMD = (
    "\"{}\"".format(os.path.join(VENV_SCRIPT_DIR_PATH, "pip.exe"))
    if IS_WINDOWS else
    "python \"{}\"".format(os.path.join(VENV_SCRIPT_DIR_PATH, "pip"))
)

END_CMD = (
    " >> \"{}\" 2>&1 || goto :error \n"
    if IS_WINDOWS else
    " >> \"{}\" 2>&1 ;\n"
).format(LOG_FPATH)

SCRIPT_EXTENSION = "bat" if IS_WINDOWS else "sh"

SCRIPT_HEADER = ["@echo off"] if IS_WINDOWS else ["set -e;"]

SCRIPT_FOOTER = ["", ":error", "  exit /b %errorlevel%"] if IS_WINDOWS else []

DULWICH_PKG = (
    res.get("dulwich_windows-0.9.8-cp27-none-any.whl")
    if IS_WINDOWS else
    res.get("dulwich-0.9.8.tar.gz")
)


# =============================================================================
# TEMPLATES FOS SCRIPTS
# =============================================================================

CREATE_VENV_CMDS_TEMPLATE = """
python "$VIRTUALENV_PATH" "$LAUNCHER_VENV_PATH"
$ACTIVATE_CMD
$PIP_CMD install "$DULWICH_PKG"
$PIP_CMD install --upgrade -r "$REQUIREMENTS_PATH"
"""

CLONE_CMDS_TEMPLATE = """
$ACTIVATE_CMD
$DULWICH_CMD clone "$OTREE_REPO" "$WRK_PATH"
"""

OPEN_TERMINAL_CMDS_TEMPLATE = """
cd "$WRK_PATH"
$TERMINAL_CMD $ACTIVATE_PATH
"""

INSTALL_REQUIEMENTS_CMDS_TEMPLATE = """
$ACTIVATE_CMD
$PIP_CMD install --upgrade -r "$REQUIREMENTS_PATH"
"""

RESET_CMDS_TEMPLATE = """
$ACTIVATE_CMD
cd "$WRK_PATH"
python "$OTREE_SCRIPT_PATH" resetdb --noinput
"""

RUN_CMDS_TEMPLATE = """
$ACTIVATE_CMD
cd "$WRK_PATH"
python "$OTREE_SCRIPT_PATH" runserver
"""

# =============================================================================
# LOGGER
# =============================================================================

logger = logging.getLogger(__file__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


# =============================================================================
# DIRECTORIES & FILES
# =============================================================================

for dpath in [LAUNCHER_DIR_PATH, LAUNCHER_TEMP_DIR_PATH]:
    if not os.path.isdir(dpath):
        os.makedirs(dpath)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

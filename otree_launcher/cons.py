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
VERSION = ("0", "3", "3")

STR_VERSION = __version__ = ".".join(VERSION)

HOME_DIR = os.path.expanduser("~")

OTREE_REPO = "https://github.com/oTree-org/oTree.git"

REQUIREMENTS_FNAME = "requirements_base.txt"

DEFAULT_OTREE_DEMO_URL = "http://localhost:8000/"

OTREE_SCRIPT_FNAME = "otree"

VENV_REQUIREMENTS_URL = (
    "https://raw.githubusercontent.com/oTree-org/oTree/master/"
    "requirements_base.txt"
)

# this servers are needed to run otree-launcher
SERVERS = ["https://github.com/", "https://pypi.python.org/"]


# =============================================================================
# PLATAFORM DEPENDENT CONSTANTS
# =============================================================================

IS_WINDOWS = sys.platform.startswith("win")

IS_OSX = sys.platform.startswith("darwin")

LAUNCHER_DIR_PATH = os.path.join(
    os.environ.get("APPDATA", HOME_DIR) if IS_WINDOWS else HOME_DIR,
    "otree launcher" if IS_WINDOWS else ".otree-launcher"
)

if IS_WINDOWS:
    # patch the path
    from .libs import winext
    os.makedirs(LAUNCHER_DIR_PATH)
    LAUNCHER_DIR_PATH = winext.shortpath(LAUNCHER_DIR_PATH)


LAUNCHER_VENV_PATH = os.path.join(LAUNCHER_DIR_PATH, "oTree")

LAUNCHER_TEMP_DIR_PATH = os.path.join(LAUNCHER_DIR_PATH, "temp")

LOG_FPATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.log")

DB_FPATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.db")

ENCODING = "UTF-8"

INTERPRETER = "" if IS_WINDOWS else "bash"

VENV_SCRIPT_DIR_PATH = os.path.join(LAUNCHER_VENV_PATH,
                                    "Scripts" if IS_WINDOWS else "bin")

ACTIVATE_PATH = (
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
python -m pip install --upgrade pip
python -m pip install "$DULWICH_PKG" --global-option="--pure"
python -m pip install --upgrade -r "$REQUIREMENTS_PATH"
"""

CLONE_CMDS_TEMPLATE = """
$ACTIVATE_CMD
$DULWICH_CMD clone "$OTREE_REPO" "$WRK_PATH"
"""

INSTALL_REQUIREMENTS_CMDS_TEMPLATE = """
$ACTIVATE_CMD
python -m pip install --upgrade -r "$REQUIREMENTS_PATH"
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

if IS_WINDOWS:
    OPEN_TERMINAL_CMDS_TEMPLATE = """
        start "$PRJ" /d "$WRK_PATH" cmd /k call "$ACTIVATE_PATH"
    """
    OPEN_FILEMANAGER_CMDS_TEMPLATE = """
        start explorer "$WRK_PATH"
    """
elif IS_OSX:
    _osx_terminal = res.get("osx_terminal.sh")
    _cmds = [
        "source $ACTIVATE_PATH",
        "cd '$WRK_PATH'",
        "echo -n -e '\\033]0;$PRJ\\007'",
        "clear",
    ]
    OPEN_TERMINAL_CMDS_TEMPLATE = """
        bash "{terminal}" "{cmds}"
    """.format(terminal=_osx_terminal, cmds="; ".join(_cmds)).lstrip()
    del _osx_terminal, _cmds

    OPEN_FILEMANAGER_CMDS_TEMPLATE = """
        open "$WRK_PATH"
    """
else:
    OPEN_TERMINAL_CMDS_TEMPLATE = """
        cd "$WRK_PATH"
        xterm -fa monaco -fs 10 -T "$PRJ" -e bash --rcfile "$ACTIVATE_PATH"
    """
    OPEN_FILEMANAGER_CMDS_TEMPLATE = """
        sh -x $$(which xdg-open) "$WRK_PATH"
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

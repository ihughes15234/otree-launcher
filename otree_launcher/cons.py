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
# COMMON IMPORTS
# =============================================================================

import sys
import os
import logging
import json
import datetime

from . import res


# =============================================================================
# PLATFORM IMPORTS
# =============================================================================

MAX_PYVERSION = (2, 7)

IS_WINDOWS = sys.platform.startswith("win")

IS_OSX = sys.platform.startswith("darwin")

winext = None

if IS_WINDOWS:
    from .libs import winext


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
with open(res.get("version.json")) as fp:
    VERSION = tuple(json.load(fp)["version"])

STR_VERSION = __version__ = ".".join(VERSION)

OTREE_REPO = "https://github.com/oTree-org/oTree.git"

REQUIREMENTS_FNAME = "requirements_base.txt"

DEFAULT_OTREE_DEMO_URL = "http://localhost:8000/"

OTREE_SCRIPT_FNAME = "otree"

VENV_REQUIREMENTS_URL = (
    "https://raw.githubusercontent.com/oTree-org/oTree/master/"
    "requirements_base.txt"
)

LASTEST_VERSION_URL = (
    "https://raw.githubusercontent.com/oTree-org/otree-launcher/master/"
    "otree_launcher/res/version.json"
)

OTREE_LAUNCHER_ZIP_URL = (
    "https://github.com/oTree-org/otree-launcher/archive/master.zip"
)

# this servers are needed to run otree-launcher
SERVERS = ["https://github.com/", "https://pypi.python.org/"]

GIT_AVAILABLE = os.system("git --version") == 0

ENCODING = "UTF-8"

TODAY = datetime.date.today()


# =============================================================================
# PLATAFORM DEPENDENT CONSTANTS
# =============================================================================

OUR_PATH = os.path.abspath(os.path.dirname(__file__))

HOME_DIR = winext.expanduser("~") if IS_WINDOWS else os.path.expanduser("~")

LAUNCHER_DIR_PATH = os.path.join(
    os.getenv("APPDATA", HOME_DIR) if IS_WINDOWS else HOME_DIR,
    "otree-launcher" if IS_WINDOWS else ".otree-launcher"
)

if IS_WINDOWS:
    # patch the path
    if not os.path.isdir(LAUNCHER_DIR_PATH):
        os.makedirs(LAUNCHER_DIR_PATH)
    LAUNCHER_DIR_PATH = winext.shortpath(LAUNCHER_DIR_PATH)
    OUR_PATH = winext.shortpath(OUR_PATH)
else:
    LAUNCHER_DIR_PATH = LAUNCHER_DIR_PATH.decode(ENCODING)
    OUR_PATH = OUR_PATH.decode(ENCODING)

LAUNCHER_VENV_PATH = os.path.join(LAUNCHER_DIR_PATH, "oTree")

LAUNCHER_TEMP_DIR_PATH = os.path.join(LAUNCHER_DIR_PATH, "temp")

LOG_DIR_PATH = os.path.join(LAUNCHER_DIR_PATH, "logs")

LOG_FPATH = os.path.join(LOG_DIR_PATH, "{}.log".format(TODAY.isoformat()))

DB_FPATH = os.path.join(LAUNCHER_DIR_PATH, "launcher.db")

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


GIT_CMD = (
    "git"
    if GIT_AVAILABLE else
    "python \"{}\"".format(os.path.join(VENV_SCRIPT_DIR_PATH, "dulwich"))
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
    res.get("packages", "dulwich_windows-0.9.8-cp27-none-any.whl")
    if IS_WINDOWS else
    res.get("packages", "dulwich-0.10.1a.tar.gz")
)

VIRTUALENV_CREATOR_PATH = res.get("packages", "virtualenv", "virtualenv.py")


# =============================================================================
# TEMPLATES FOS SCRIPTS
# =============================================================================

CREATE_VENV_CMDS_TEMPLATE = """
python "$VIRTUALENV_CREATOR_PATH" "$LAUNCHER_VENV_PATH"
$ACTIVATE_CMD
python -m pip install --upgrade pip
python -m pip install "$DULWICH_PKG" --global-option="--pure"
python -m pip install --upgrade -r "$REQUIREMENTS_PATH"
"""

CLONE_CMDS_TEMPLATE = """
$ACTIVATE_CMD
$GIT_CMD clone "$OTREE_REPO" "$WRK_PATH"
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
    _osx_terminal = res.get("scripts", "osx_terminal.sh")
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

for dpath in [LAUNCHER_DIR_PATH, LAUNCHER_TEMP_DIR_PATH, LOG_DIR_PATH]:
    if not os.path.isdir(dpath):
        os.makedirs(dpath)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

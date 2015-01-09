#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


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
import string
import select
import codecs
import tempfile

from libs import sh, virtualenv


# =============================================================================
# CONSTANTS
# =============================================================================

PRJ = "install"

DOC = __doc__

# : The project version as tuple of strings
VERSION = ("0", "1")

# : The project version as string
STR_VERSION = __version__ = ".".join(VERSION)

OTREE_REPO = "git@github.com:oTree-org/oTree.git"

OTREE_DIR = "oTree"

REQUIREMENTS_FILE = "requirements_base.txt"

IS_WINDOWS = sys.platform.startswith("win")

ENCODING = "UTF-8"

INTERPRETER = "cmd" if IS_WINDOWS else "bash"

PRINT = "@echo" if IS_WINDOWS else "echo"

END_CMD = "\n" if IS_WINDOWS else ";\n"

CMDS = """
python $VIRTUALENV_PATH $WRK_PATH
$ACTIVATE
git clone $REPO $OTREE_PATH
pip install --upgrade -r $REQUIREMENTS_PATH
cd $OTREE_PATH
python otree resetdb --noinput
python otree runserver
"""

RUNNER = "run.bat" if IS_WINDOWS else "run.sh"


RUN_CMDS = """
$ACTIVATE
cd $OTREE_PATH
python otree runserver
"""

# =============================================================================
# LOGGER
# =============================================================================

def get_logger():
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

logger = get_logger()


# =============================================================================
# SYSTEM DEPENDENCIES CHECK
# =============================================================================

# sde = system dependencies errors
_sde = []
try:
    sh.git(help=True)
except sh.CommandNotFound as err:
    _sde.append(
        "'git' command not found. For install see: http://git-scm.com/"
    )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

@contextlib.contextmanager
def tempscript(content):
    fd, fname = None, None
    try:
        fd, fname = tempfile.mkstemp(suffix=PRJ)
        with codecs.open(fname, "w", encoding=ENCODING) as fp:
            fp.write(content)
        yield fname
    finally:
        if fd:
            os.close(fd)


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


def generate_script(wrkpath):
    # vars
    activate_cmd = None
    if IS_WINDOWS:
        activate_cmd =  os.path.join(wrkpath, "Scripts", "activate")
    else:
        activate_cmd = "source {}".format(
            os.path.join(wrkpath, "bin", "activate")
        )

    otree_path = os.path.join(wrkpath, OTREE_DIR)
    requirements_path = os.path.join(otree_path, REQUIREMENTS_FILE)

    tpl = string.Template(CMDS.strip())
    src = tpl.substitute(
        WRK_PATH=wrkpath,
        VIRTUALENV_PATH=os.path.abspath(virtualenv.__file__),
        ACTIVATE=activate_cmd,
        REPO=OTREE_REPO,
        OTREE_PATH=otree_path,
        REQUIREMENTS_PATH=requirements_path
    )
    script = "".join([
        "{}{}".format(line, END_CMD) for line in src.splitlines()
    ])
    return script


def logcall(popenargs, logger, stdout_log_level=logging.INFO,
         stderr_log_level=logging.ERROR, **kwargs):
    """
    Variant of subprocess.call that accepts a logger instead of stdout/stderr,
    and logs stdout messages via logger.debug and stderr messages via
    logger.error.
    """
    child = subprocess.Popen(popenargs, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
    log_level = {
        child.stdout: stdout_log_level,
        child.stderr: stderr_log_level
    }

    def check_io():
        ready_to_read = select.select(
            [child.stdout, child.stderr], [], [], 1000
        )[0]
        for io in ready_to_read:
            line = io.readline()
            msg = line[:-1]
            if msg:
                logger.log(log_level[io], msg)

    # keep checking stdout/stderr until the child exits
    while child.poll() is None:
        check_io()
    check_io() # check again to catch anything after the process exits
    return child.wait()


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def validate_system_dependencies():
    global _sde
    if _sde:
        errors = "\n\t".join(SYSTEM_DEPENDENCIES_ERRORS)
        msg = "System Error found:\n\t{}".format(errors)
        raise SystemError(msg)


def install_otree(wrkpath, out=None):
    script = generate_script(wrkpath)
    import ipdb; ipdb.set_trace()
    with tempscript(script) as script_path:
        command = [INTERPRETER, script_path]
        if isinstance(out, logging.Logger):
            return logcall(command, out)
        else:
            return subprocess.call(command, stdout=out, stdin=out)


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
    runner_path = os.path.join(wrkpath, OTREE_DIR, RUNNER)
    logger.info("Initiating oTree installer on '{}'".format(wrkpath))
    install_otree(wrkpath, logger)
    logger.info("If you want to run again execute {}".format(runner_path))


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()

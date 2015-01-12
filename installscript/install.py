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
import shutil
import logging
import argparse
import contextlib
import string
import select
import codecs
import webbrowser
import atexit
import time
import uuid

from libs import virtualenv


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

OTREE_SPAN_SLEEP = 5

DEFAULT_OTREE_URL = "http://localhost:8000/"

# PLATAFORM DEPENDENT CONSTANTS

IS_WINDOWS = sys.platform.startswith("win")

ENCODING = "UTF-8"

DULWICH_PKG = "dulwich-windows" if IS_WINDOWS else "dulwich"

INTERPRETER = "cmd" if IS_WINDOWS else "bash"

END_CMD = "\n" if IS_WINDOWS else ";\n"


SCRIPT_EXTENSION = "bat" if IS_WINDOWS else "sh"

# SCRIPTS TEMPLATES


INSTALL_CMDS = """
python $VIRTUALENV_PATH $WRK_PATH
$ACTIVATE
pip install $DULWICH_PKG
dulwich clone $REPO $OTREE_PATH
pip install --upgrade -r $REQUIREMENTS_PATH
cd $OTREE_PATH
python otree resetdb --noinput
"""

RUNNER = "run.{}".format(SCRIPT_EXTENSION)

RUNNER_CMDS = """
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
# HELPER FUNCTIONS
# =============================================================================

@contextlib.contextmanager
def tempscript(wrkpath, content):
    fname = "installer_{}.{}".format(uuid.uuid4().int, SCRIPT_EXTENSION)
    fpath = os.path.join(wrkpath, fname)
    try:
        with codecs.open(fpath, "w", encoding=ENCODING) as fp:
            fp.write(content)
        yield fpath
    finally:
        if os.path.isfile(fpath):
            os.remove(fpath)


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


def render(template, wrkpath):
    # vars
    activate_cmd = None
    if IS_WINDOWS:
        activate_cmd = os.path.join(wrkpath, "Scripts", "activate")
    else:
        activate_cmd = "source {}".format(
            os.path.join(wrkpath, "bin", "activate")
        )

    otree_path = os.path.join(wrkpath, OTREE_DIR)
    requirements_path = os.path.join(otree_path, REQUIREMENTS_FILE)

    src = string.Template(template.strip()).substitute(
        WRK_PATH=wrkpath,
        VIRTUALENV_PATH=os.path.abspath(virtualenv.__file__),
        ACTIVATE=activate_cmd,
        REPO=OTREE_REPO,
        OTREE_PATH=otree_path,
        REQUIREMENTS_PATH=requirements_path,
        DULWICH_PKG=DULWICH_PKG
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

    # check again to catch anything after the process exits
    check_io()
    return child.wait()


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def install_otree(wrkpath, out=None):
    installer_src = render(INSTALL_CMDS, wrkpath)
    retcode = 0
    with tempscript(wrkpath, installer_src) as installer_path:
        command = [INTERPRETER, installer_path]
        if isinstance(out, logging.Logger):
            retcode = logcall(command, out)
        else:
            retcode = subprocess.call(command, stdout=out, stdin=out)
    if not retcode:
        runner_src = render(RUNNER_CMDS, wrkpath)
        runner_path = os.path.join(wrkpath, OTREE_DIR, RUNNER)
        with codecs.open(runner_path, "w", encoding=ENCODING) as fp:
            fp.write(runner_src)
    return retcode


# =============================================================================
# FUNCTIONS
# =============================================================================

def main():

    # retrieve parser
    parser = get_parser()
    args = parser.parse_args()

    # start install
    wrkpath = args.wrkpath
    runner_path = os.path.join(wrkpath, OTREE_DIR, RUNNER)
    logger.info("Initiating oTree installer on '{}'".format(wrkpath))
    install_otree(wrkpath, logger)

    # run
    command = [INTERPRETER, runner_path]
    logger.info("Starting oTree on '{}'".format(wrkpath))
    time.sleep(OTREE_SPAN_SLEEP)
    proc = subprocess.Popen(command)

    logger.info("Lunching webbrowser...")
    time.sleep(OTREE_SPAN_SLEEP)
    webbrowser.open_new_tab(DEFAULT_OTREE_URL)

    # clean
    def clean(proc):
        if proc.returncode is None:
            proc.kill()

        msg = "If you want to run again execute {}".format(runner_path)
        msglen = len(msg)

        logger.info("=" * msglen)
        logger.info(msg)
        logger.info("=" * msglen)

    atexit.register(clean, proc)

    proc.wait()

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# FUTURE
# =============================================================================

from __future__ import unicode_literals


# =============================================================================
# DOCS
# =============================================================================

__doc__ = """Installer logic

"""


# =============================================================================
# IMPORTS
# =============================================================================

import os
import subprocess
import string
import webbrowser
import zipfile
import atexit
import time
import datetime
import threading

from . import cons, ctx
from .libs.virtualenv import virtualenv


# =============================================================================
# LOGGER
# =============================================================================

logger = cons.logger


# =============================================================================
# EXCEPTION
# =============================================================================

class InstallError(Exception):
    """This exception is raised when something gone wrong on install logic

    """

    def __init__(self, code):
        self.code = code
        super(InstallError, self).__init__(
            "Exit code with value '{}'".format(code)
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def kill_proc(proc):
    if cons.IS_WINDOWS:
        proc = call(["TASKKILL", "/F", "/PID", str(proc.pid), "/T"])
        proc.communicate()
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)


def clean_proc(proc):
    """Clean process if is still runing on exit"""
    if proc.returncode is None:
        kill_proc(proc)


def call(command, sleep=1, *args, **kwargs):
    """Call an external command"""
    cleaned_cmd = [cmd.strip() for cmd in command if cmd.strip()]
    if cons.IS_WINDOWS:
        proc = subprocess.Popen(cleaned_cmd, *args, **kwargs)
    else:
        proc = subprocess.Popen(
            cleaned_cmd, preexec_fn=os.setsid, *args, **kwargs
        )
    atexit.register(clean_proc, proc)
    time.sleep(sleep)
    return proc


def render(template, wrkpath):
    """Render template acoring the working path

    """
    # vars
    src = string.Template(template.strip()).substitute(**{
        "WRK_PATH": wrkpath,
        "VIRTUALENV_PATH": os.path.abspath(virtualenv.__file__),
        "REQUIREMENTS_PATH": os.path.join(wrkpath, cons.REQUIREMENTS_FNAME),
        "PIP_CMD": cons.PIP_CMD,
        "DULWICH_PKG": cons.DULWICH_PKG,
        "LAUNCHER_VENV_PATH": cons.LAUNCHER_VENV_PATH,
        "DULWICH_CMD": cons.DULWICH_CMD,
        "ACTIVATE_CMD": cons.ACTIVATE_CMD,
        "OTREE_REPO": cons.OTREE_REPO,
        "OTREE_SCRIPT_PATH": os.path.join(wrkpath, cons.OTREE_SCRIPT_FNAME)
    })
    script = "".join(
        ["\n".join(cons.SCRIPT_HEADER), "\n"] +
        ["{}{}".format(line, cons.END_CMD) for line in src.splitlines()] +
        ["\n".join(cons.SCRIPT_FOOTER), "\n"]
    ).strip() + "\n"
    return script


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def create_virtualenv():
    """Create otree virtualenv

    """
    logger.info(
        "Creating virtualenv on '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )
    with ctx.tempfile("venv_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating virtualenv install script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CREATE_VENV_CMDS_TEMPLATE,
                         cons.LAUNCHER_VENV_PATH)
            fp.write(src)
        logger.info("Creating venv please wait"
                    "(this can be take some minutes)...")
        return call([cons.INTERPRETER, fpath])


def clone(wrkpath):
    """Clone otree code into working dir

    """
    logger.info("Clone on '{}'...".format(wrkpath))
    with ctx.tempfile("cloner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating cloner script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CLONE_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Clonning...")
        return call([cons.INTERPRETER, fpath])


def install_requirements(wrkpath):
    logger.info(
        "Installing requirements of '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )
    with ctx.tempfile("req_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating requirements install script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.INSTALL_REQUIEMENTS_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Installing please wait"
                    "(this can be take some minutes)...")
        return call([cons.INTERPRETER, fpath])


def reset_db(wrkpath):
    """Reset the database of the oTree installation

    """
    logger.info("Reset oTree on '{}'...".format(wrkpath))
    with ctx.tempfile("reseter", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating reseter script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RESET_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Reseting (this can be take some minutes)...")
        return call([cons.INTERPRETER, fpath])


def runserver(wrkpath):
    """Run otree of the working path installation

    """
    logger.info("Running otree on'{}'...".format(wrkpath))
    with ctx.tempfile("runner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating runner script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RUN_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Starting...")
        return  call([cons.INTERPRETER, fpath])


def open_webbrowser(url=cons.DEFAULT_OTREE_DEMO_URL):
    """Open the web browser on the given url

    """
    logger.info("Launching webbrowser...")
    time.sleep(cons.OTREE_SPAN_SLEEP)
    webbrowser.open_new_tab(url)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

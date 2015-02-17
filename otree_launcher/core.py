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
import shlex

from . import cons, ctx, db
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
    if proc.poll() is None:
        kill_proc(proc)


def call(command, *args, **kwargs):
    """Call an external command"""
    cleaned_cmd = [cmd.strip() for cmd in command if cmd.strip()]
    if cons.IS_WINDOWS:
        proc = subprocess.Popen(cleaned_cmd, *args, **kwargs)
    else:
        proc = subprocess.Popen(
            cleaned_cmd, preexec_fn=os.setsid, *args, **kwargs
        )
    atexit.register(clean_proc, proc)
    return proc


def render(template, wrkpath, **kwargs):
    """Render template acoring the working path

    """
    # vars
    context = {
        k:v for k, v in vars(cons).items()
        if not k.startswith("_") and k.isupper()
    }
    context.update({
        "WRK_PATH": wrkpath,
        "VIRTUALENV_PATH": os.path.abspath(virtualenv.__file__),
        "REQUIREMENTS_PATH": os.path.join(wrkpath, cons.REQUIREMENTS_FNAME),
        "OTREE_SCRIPT_PATH": os.path.join(wrkpath, cons.OTREE_SCRIPT_FNAME),
    })
    context.update(kwargs)

    src = string.Template(template.strip()).substitute(**context)
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
        "Creating virtualenv in '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )

    reqpath = None
    with ctx.tempfile("requirements", "txt") as fpath:
        logger.info("Downloading requirements file...")
        with ctx.urlget(cons.VENV_REQUIREMENTS_URL) as response:
            with ctx.open(fpath, "w") as fp:
                fp.write(response.read())
        reqpath = fpath

    with ctx.tempfile("venv_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating virtualenv install script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CREATE_VENV_CMDS_TEMPLATE,
                         cons.LAUNCHER_VENV_PATH, REQUIREMENTS_PATH=reqpath)
            fp.write(src)
        logger.info("Creating venv, please wait"
                    " (this may take a few minutes)...")
        return call([cons.INTERPRETER, fpath])


def clone(wrkpath):
    """Clone otree code into working dir

    """
    logger.info("Cloning into '{}'...".format(wrkpath))
    with ctx.tempfile("cloner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating cloner script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.CLONE_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Cloning...")
        return call([cons.INTERPRETER, fpath])


def install_requirements(wrkpath):
    logger.info(
        "Installing requirements in '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )
    with ctx.tempfile("req_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating requirements install script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.INSTALL_REQUIEMENTS_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Installing, please wait"
                    "(this may take a few minutes)...")
        return call([cons.INTERPRETER, fpath])


def reset_db(wrkpath):
    """Reset the database of the oTree installation

    """
    logger.info("Reset oTree in '{}'...".format(wrkpath))
    with ctx.tempfile("reseter", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating reset script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RESET_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Resetting (please wait)...")
        return call([cons.INTERPRETER, fpath])


def runserver(wrkpath):
    """Run otree of the working path installation

    """
    logger.info("Running oTree in '{}'...".format(wrkpath))
    with ctx.tempfile("runner", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating runner script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.RUN_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Starting...")
        return call([cons.INTERPRETER, fpath])


def open_terminal(wrkpath):
    """Open a new terminal activating the virtualenv

    """
    logger.info("Opening terminal in '{}'...".format(wrkpath))
    with ctx.tempfile("open_terminal", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating open terminal script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.OPEN_TERMINAL_CMDS_TEMPLATE, wrkpath)
            fp.write(src)
        logger.info("Launching Terminal...")
        return call([cons.INTERPRETER, fpath])


def open_webbrowser(url=cons.DEFAULT_OTREE_DEMO_URL):
    """Open the web browser on the given url

    """
    logger.info("Launching web browser...")
    time.sleep(cons.OTREE_SPAN_SLEEP)
    webbrowser.open_new_tab(url)


def get_conf():
    """Get the configuration of oTree Launcher"""
    if db.Configuration.select().count():
            return db.Configuration.select().get()
    return db.Configuration.create()


def logfile_fp():
    """Open and return the log file used for external process"""

    logger.info("Opening log file '{}'...".format(cons.LOG_FPATH))

    with open(cons.LOG_FPATH, "w"):
        pass

    fp = open(cons.LOG_FPATH)
    fp.seek(0, 2)
    return fp


def clean_tempdir():
    """Destroy all files inside the temporary directory"""
    logger.info("Cleaning temp dir '{}'".format(cons.LAUNCHER_TEMP_DIR_PATH))
    for fname in os.listdir(cons.LAUNCHER_TEMP_DIR_PATH):
        fpath = os.path.join(cons.LAUNCHER_TEMP_DIR_PATH, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)

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
        call(["TASKKILL", "/F", "/PID", str(proc.pid), "/T"])
    else:
        import signal
        os.killpg(proc.pid, signal.SIGTERM)


def clean_proc(proc):
    """Clean process if is still runing on exit"""
    if proc.returncode is None:
        kill_proc(proc)


def call(command, span=False, *args, **kwargs):
    """Call an external command"""
    cleaned_cmd = [cmd.strip() for cmd in command if cmd.strip()]
    if cons.IS_WINDOWS:
        proc = subprocess.Popen(cleaned_cmd, *args, **kwargs)
    else:
        proc = subprocess.Popen(
            cleaned_cmd, preexec_fn=os.setsid, *args, **kwargs
        )
    while proc.returncode is None and not span:
        time.sleep(1)
    return proc


def render(template, wrkpath):
    """Render template acoring the working path

    """
    # vars
    activate_cmd = pip = None
    if cons.IS_WINDOWS:
        activate_cmd = "call \"{}\"".format(
            os.path.join(wrkpath, cons.VENV_SCRIPT_DIR, "activate.bat")
        )
        pip = "\"{}\"".format(
            os.path.join(wrkpath, cons.VENV_SCRIPT_DIR, "pip.exe")
        )
    else:
        activate_cmd = "source \"{}\"".format(
            os.path.join(wrkpath, cons.VENV_SCRIPT_DIR, "activate")
        )
        pip = "python \"{}\"".format(
            os.path.join(wrkpath, cons.VENV_SCRIPT_DIR, "pip")
        )

    otree_path = os.path.join(wrkpath, cons.OTREE_DIR)
    requirements_path = os.path.join(otree_path, cons.REQUIREMENTS_FNAME)
    runscript = os.path.join(otree_path, "otree")

    pip_path = os.path.join(wrkpath, cons.VENV_SCRIPT_DIR, "pip")

    src = string.Template(template.strip()).substitute(
        WRK_PATH=wrkpath,
        VIRTUALENV_PATH=os.path.abspath(virtualenv.__file__),
        ACTIVATE=activate_cmd,
        OTREE_PATH=otree_path,
        REQUIREMENTS_PATH=requirements_path,
        RUNSCRIPT=runscript,
        PIP=pip
    )
    script = "".join(
        ["\n".join(cons.SCRIPT_HEADER), "\n"] +
        ["{}{}".format(line, cons.END_CMD) for line in src.splitlines()] +
        ["\n".join(cons.SCRIPT_FOOTER), "\n"]
    ).strip()
    return script


def resolve_runner_path(wrkpath):
    """Resolve the location of the runner script"""
    return os.path.join(
        wrkpath, cons.VENV_SCRIPT_DIR, cons.RUNNER_SCRIPT_FNAME
    )


def resolve_reseter_path(wrkpath):
    """Resolve the location of the reseter script"""
    return os.path.join(
        wrkpath, cons.VENV_SCRIPT_DIR, cons.RESET_SCRIPT_FNAME
    )


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def download(wrkpath):
    """Download otree code into working dir

    """
    logger.info("Downloading oTree on '{}'...".format(wrkpath))
    with ctx.urlget(cons.OTREE_CODE_URL) as response:
        with ctx.tempfile(wrkpath, "otree", "zip") as fpath:
            with ctx.open(fpath, "wb", encoding=None) as fp:
                fp.write(response.read())
            with zipfile.ZipFile(fpath, "r") as zfp:
                zfp.extractall(wrkpath)
    otree_dwld_path = os.path.join(wrkpath, cons.DOWNLOAD_OTREE_DIR)
    otreepath = os.path.join(wrkpath, cons.OTREE_DIR)
    os.rename(otree_dwld_path, otreepath)


def install(wrkpath):
    """Install oTree on a given *wrkpath*

    """
    logger.info("Initiating oTree installer on '{}'...".format(wrkpath))
    retcode = 0
    with ctx.tempfile(wrkpath, "installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating install script...")
        with ctx.open(fpath, "w") as fp:
            installer_src = render(cons.INSTALL_CMDS_TEMPLATE, wrkpath)
            fp.write(installer_src)
        command = [cons.INTERPRETER, fpath]
        logger.info("Install please wait (this can be take some minutes)...")
        retcode = call(command).returncode
    if not retcode:
        logger.info("Creating reset script...")
        reseter_src = render(cons.RESET_CMDS_TEMPLATE, wrkpath)
        reseter_path = resolve_reseter_path(wrkpath)
        with ctx.open(reseter_path, "w") as fp:
            fp.write(reseter_src)
        logger.info("Creating run script...")
        runner_src = render(cons.RUNNER_CMDS_TEMPLATE, wrkpath)
        runner_path = resolve_runner_path(wrkpath)
        with ctx.open(runner_path, "w") as fp:
            fp.write(runner_src)
    if retcode:
        raise InstallError(retcode)
    logger.info("Registering...")
    deploy = db.Deploy(path=wrkpath)
    deploy.save()


def reset(wrkpath):
    """Execute the reset script of the working path installation

    """
    logger.info("Reset oTree on '{}'...".format(wrkpath))
    reseter_path = resolve_reseter_path(wrkpath)
    command = [cons.INTERPRETER, reseter_path]
    retcode = call(command, span=False).returncode
    if not retcode:
        db.Deploy.update(
            last_update=datetime.datetime.now()
        ).where(db.Deploy.path == wrkpath).execute()
    return retcode


def execute(wrkpath):
    """Execute the runner script of the working path installation

    """
    logger.info("Running otree on'{}'...".format(wrkpath))
    runner_path = resolve_runner_path(wrkpath)
    command = [cons.INTERPRETER, runner_path]
    proc = call(command, span=True)
    atexit.register(clean_proc, proc)
    return proc


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

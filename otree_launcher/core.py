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

from . import cons, ctx
from .libs import virtualenv


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

def call(command, span=False, *args, **kwargs):
    """Call an external command"""
    cleaned_cmd = [cmd.strip() for cmd in command if cmd.strip()]
    if span:
        proc = subprocess.Popen(cleaned_cmd, *args, **kwargs)
        return proc
    retcode = subprocess.call(cleaned_cmd, *args, **kwargs)
    return retcode


def render(template, wrkpath):
    """Render template acoring the working path

    """
    # vars
    activate_cmd = None
    if cons.IS_WINDOWS:
        activate_cmd = "call {}".format(
            os.path.join(wrkpath, "Scripts", "activate.bat")
        )
    else:
        activate_cmd = "source {}".format(
            os.path.join(wrkpath, "bin", "activate")
        )

    otree_path = os.path.join(wrkpath, cons.OTREE_DIR)
    requirements_path = os.path.join(otree_path, cons.REQUIREMENTS_FNAME)
    runscript = os.path.join(otree_path, "otree")

    src = string.Template(template.strip()).substitute(
        WRK_PATH=wrkpath,
        VIRTUALENV_PATH=os.path.abspath(virtualenv.__file__),
        ACTIVATE=activate_cmd,
        OTREE_PATH=otree_path,
        REQUIREMENTS_PATH=requirements_path,
        RUNSCRIPT=runscript
    )
    script = "".join(
        ["\n".join(cons.SCRIPT_HEADER), "\n"] +
        ["{}{}".format(line, cons.END_CMD) for line in src.splitlines()] +
        ["\n".join(cons.SCRIPT_FOOTER), "\n"]
    ).strip()
    return script


# =============================================================================
# LOGIC ITSELF
# =============================================================================

def download(wrkpath):
    """Download otree code into working dir

    """
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
    retcode = 0
    with ctx.tempfile(wrkpath, "installer", cons.SCRIPT_EXTENSION) as fpath:
        with ctx.open(fpath, "w") as fp:
            installer_src = render(cons.INSTALL_CMDS_TEMPLATE, wrkpath)
            fp.write(installer_src)
        command = [cons.INTERPRETER, fpath]
        retcode = call(command)
    if not retcode:
        runner_src = render(cons.RUNNER_CMDS_TEMPLATE, wrkpath)
        runner_path = os.path.join(
            wrkpath, cons.OTREE_DIR, cons.RUNNER_SCRIPT_FNAME
        )
        with ctx.open(runner_path, "w") as fp:
            fp.write(runner_src)
    if retcode:
        raise InstallError(retcode)


def execute(wrkpath):
    """Execute the runner script of the working path installation

    """
    runner_path = os.path.join(
        wrkpath, cons.OTREE_DIR, cons.RUNNER_SCRIPT_FNAME
    )
    command = [cons.INTERPRETER, runner_path]
    return call(command, span=True)


def open_webbrowser(url=cons.DEFAULT_OTREE_DEMO_URL):
    """Open the web browser on the given url

    """
    webbrowser.open_new_tab(url)


def full_install_and_run(wrkpath):
    """Execute all the commands of instalation and run the installed proyect
    on finish

    """
    logger.info("Downloading oTree on '{}'".format(wrkpath))
    download(wrkpath)

    logger.info("Initiating oTree installer on '{}'".format(wrkpath))
    install(wrkpath)

    # run
    proc = execute(wrkpath)

    logger.info("Lunching webbrowser...")
    time.sleep(cons.OTREE_SPAN_SLEEP)
    open_webbrowser()

    # clean
    def clean(proc):
        if proc.returncode is None:
            proc.kill()

        runner_path = os.path.join(
            wrkpath, cons.OTREE_DIR, cons.RUNNER_SCRIPT_FNAME
        )
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
    print(__doc__)
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
import atexit
import urllib2
import urlparse
import json
import sys

from . import cons, ctx, db
from .libs import dpaste


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

def check_connectivity(timeout=1):
    """Check if all servers needed for use oTree-launcher are online

    """
    errors = []
    for server in cons.SERVERS:
        try:
            urllib2.urlopen(server, timeout=timeout)
        except urllib2.URLError:
            host = urlparse.urlsplit(server).netloc
            errors.append("'{}' is unreachable".format(host))
    if errors:
        errors_joined = "\n  ".join(errors)
        msg = "Check your internet connection\n  {}".format(errors_joined)
        raise IOError(msg)


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
        win_cmd = "{} < Nul".format(" ".join(cleaned_cmd))
        proc = subprocess.Popen(win_cmd, shell=True, *args, **kwargs)
    else:
        proc = subprocess.Popen(
            cleaned_cmd, preexec_fn=os.setsid, *args, **kwargs
        )
    atexit.register(clean_proc, proc)
    return proc


def render(template, wrkpath, decorate=True, **kwargs):
    """Render template acoring the working path

    """
    # vars
    context = {
        k: v for k, v in vars(cons).items()
        if not k.startswith("_") and k.isupper()
    }
    context.update({
        "WRK_PATH": wrkpath.replace("/", os.path.sep),
        "REQUIREMENTS_PATH": os.path.join(wrkpath, cons.REQUIREMENTS_FNAME),
        "OTREE_SCRIPT_PATH": os.path.join(wrkpath, cons.OTREE_SCRIPT_FNAME),
    })
    context.update(kwargs)

    src = string.Template(template.strip()).substitute(**context)

    if decorate:
        script = "".join(
            ["\n".join(cons.SCRIPT_HEADER), "\n"] +
            ["{}{}".format(l.strip(), cons.END_CMD) for l in src.splitlines()] +
            ["\n".join(cons.SCRIPT_FOOTER), "\n"]
        )
    else:
        script = "\n".join([l.strip() for l in src.splitlines()])
    return script.strip() + "\n"


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
    """Intall the requirements of the given deploy

    """
    logger.info(
        "Installing requirements in '{}'...".format(cons.LAUNCHER_VENV_PATH)
    )
    with ctx.tempfile("req_installer", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating requirements install script...")
        with ctx.open(fpath, "w") as fp:
            src = render(cons.INSTALL_REQUIREMENTS_CMDS_TEMPLATE, wrkpath)
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
            src = render(
                cons.OPEN_TERMINAL_CMDS_TEMPLATE, wrkpath, decorate=False
            )
            fp.write(src)
        logger.info("Launching Terminal...")
        return call([cons.INTERPRETER, fpath])

def open_filemanager(wrkpath):
    """Open a new terminal activating the virtualenv

    """
    logger.info("Opening filemanager in '{}'...".format(wrkpath))
    with ctx.tempfile("open_filemanager", cons.SCRIPT_EXTENSION) as fpath:
        logger.info("Creating open filemanager script...")
        with ctx.open(fpath, "w") as fp:
            src = render(
                cons.OPEN_FILEMANAGER_CMDS_TEMPLATE, wrkpath, decorate=False
            )
            fp.write(src)
        logger.info("Launching filemanager...")
        return call([cons.INTERPRETER, fpath])


def get_conf():
    """Get the configuration of oTree Launcher"""
    if db.Configuration.select().count():
            return db.Configuration.select().get()
    return db.Configuration.create()


def logfile_fp(rewind=False):
    """Open and return the log file used for external process"""

    logger.info("Opening log file '{}'...".format(cons.LOG_FPATH))

    if not os.path.exists(cons.LOG_FPATH):
        with open(cons.LOG_FPATH, "w"):
            pass

    fp = open(cons.LOG_FPATH)
    if not rewind:
        fp.seek(0, 2)
    return fp


def clean_tempdir():
    """Destroy all files inside the temporary directory"""
    logger.info("Cleaning temp dir '{}'".format(cons.LAUNCHER_TEMP_DIR_PATH))
    for fname in os.listdir(cons.LAUNCHER_TEMP_DIR_PATH):
        fpath = os.path.join(cons.LAUNCHER_TEMP_DIR_PATH, fname)
        if os.path.isfile(fpath):
            os.remove(fpath)


def check_upgrade():
    """Chek if a new version of oTree-Launcher is available and if mandatory
    to upgrade the program

    Returns: last_version, is_new, mandatory
    """
    version = list(cons.VERSION)
    with ctx.urlget(cons.LASTEST_VERSION_URL) as response:
        data = json.load(response)

        lversion = data["version"]
        str_lversion = ".".join(lversion)

        exists_upgrade = version < lversion

        mcondition = data["mandatory"]["condition"]
        mvalue = data["mandatory"]["value"]

        mandatory = {
            "==": version == mvalue,
            "<": version < mvalue,
            "<=": version <= mvalue,
            ">": version > mvalue,
            ">=": version >= mvalue,
            "!=": version != mvalue,
            "in": version in mvalue
        }[mcondition]

        return str_lversion, exists_upgrade, mandatory


def check_py_version():
    """Check if python version is ok for oTree-Launcher

    Returns: is_version_allowed(boolean), version_indo, executable_path

    """
    allowed = (cons.MAX_PYVERSION == sys.version_info[:2])
    info = (allowed, sys.version, sys.executable)
    return info


def check_our_path():
    """Check if the oTree-Launcher is in valid path"""
    if " " in cons.OUR_PATH:
        return False
    try:
        cons.OUR_PATH.encode("ascii")
    except UnicodeError:
        return False
    return True


def publish_log():
    """Publish all the content of the oTree-Launcher log in dpaste"""
    fp = None
    try:
        fp = logfile_fp(rewind=True)
        return dpaste.paste(fp.read(), expiry_days=60)
    except:
        pass
    finally:
        if not fp.closed:
            fp.close()
    return ""


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print(__doc__)
